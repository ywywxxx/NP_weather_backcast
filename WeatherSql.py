import mysql.connector


class WeatherSql:
    """
    Only input: name

    Creates its own MySQL connection + cursor.
    On init: ensures two tables exist:
      - {name}_forecast
      - {name}_backcast

    Methods:
      - insert_forecast(data)
      - insert_backcast(data)
    """

    # -------------------------
    # init / connection
    # -------------------------
    def __init__(
        self,
        name: str,
        host: str = "127.0.0.1",
        port: int = 3306,
        user: str = "weather_writer",
        password: str = "1NPS_weather_writer!",
        database: str = "weather",
        autocommit: bool = True,
    ):
        self.name = name
        self.forecast_table = f"{name}_forecast"
        self.backcast_table = f"{name}_backcast"

        self.conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
        )
        self.conn.autocommit = autocommit
        self.cur = self.conn.cursor()

        # ensure tables exist
        if not self.table_exists(self.forecast_table):
            self.create_forecast_table()

        if not self.table_exists(self.backcast_table):
            self.create_backcast_table()

    def close(self):
        try:
            self.cur.close()
        finally:
            self.conn.close()

    # -------------------------
    # 1) table exists
    # -------------------------
    def table_exists(self, table: str) -> bool:
        self.cur.execute("SHOW TABLES LIKE %s;", (table,))
        return self.cur.fetchone() is not None

    # -------------------------
    # 2) create forecast table
    # -------------------------
    def create_forecast_table(self):
        table = self.forecast_table
        sql = f"""
        CREATE TABLE {table} (
          predictor_date DATE NOT NULL,
          predictor_step SMALLINT UNSIGNED NOT NULL,

          predictee_date DATE NOT NULL,
          predictee_step SMALLINT UNSIGNED NOT NULL,

          has_rain TINYINT(1) NOT NULL DEFAULT 0,
          has_snow TINYINT(1) NOT NULL DEFAULT 0,

          temp_c_mean DOUBLE,
          temp_c_min  DOUBLE,
          temp_c_max  DOUBLE,

          precip_prob_max DOUBLE,
          wind_kmh_mean DOUBLE,
          wind_dir_mode CHAR(3),

          shortforecast_mode VARCHAR(64),

          skycover_mean DOUBLE,
          snowlevel_mean DOUBLE,

          snowfallamount_sum DOUBLE,
          quantitativeprecipitation_sum DOUBLE,
          iceaccumulation_sum DOUBLE,

          PRIMARY KEY (
            predictor_date, predictor_step,
            predictee_date, predictee_step
          ),

          INDEX idx_predictor (predictor_date, predictor_step),
          INDEX idx_predictee (predictee_date, predictee_step)
        ) ENGINE=InnoDB;
        """
        self.cur.execute(sql)

    # -------------------------
    # 3) build forecast insert
    # -------------------------
    def build_forecast_insert_sql(self, data: dict):
        table = self.forecast_table
        predictor_date, predictor_step, predictee_date, predictee_step = data["group_key"]

        sql = f"""
        INSERT IGNORE INTO {table} (
            predictor_date, predictor_step,
            predictee_date, predictee_step,
            has_rain, has_snow,
            temp_c_mean, temp_c_min, temp_c_max,
            precip_prob_max,
            wind_kmh_mean, wind_dir_mode,
            shortforecast_mode,
            skycover_mean, snowlevel_mean,
            snowfallamount_sum,
            quantitativeprecipitation_sum,
            iceaccumulation_sum
        ) VALUES (
            %s, %s, %s, %s,
            %s, %s,
            %s, %s, %s,
            %s,
            %s, %s,
            %s,
            %s, %s,
            %s,
            %s,
            %s
        );
        """

        values = (
            predictor_date,
            predictor_step,
            predictee_date,
            predictee_step,
            data["has_rain"],
            data["has_snow"],
            data["temp_C_mean"],
            data["temp_C_min"],
            data["temp_C_max"],
            data["precip_prob_max"],
            data["wind_kmh_mean"],
            data["wind_dir_mode"],
            data["shortForecast_mode"],
            data["skyCover_mean"],
            data["snowLevel_mean"],
            data["snowfallAmount_sum"],
            data["quantitativePrecipitation_sum"],
            data["iceAccumulation_sum"],
        )

        return sql, values

    # -------------------------
    # 4) create backcast table
    # -------------------------
    def create_backcast_table(self):
        table = self.backcast_table
        sql = f"""
        CREATE TABLE {table} (
          lat DOUBLE NOT NULL,
          lon DOUBLE NOT NULL,
          tz  VARCHAR(8),
          date DATE NOT NULL,
          units VARCHAR(16),

          cloud_cover_afternoon DOUBLE,
          humidity_afternoon DOUBLE,
          precipitation_total DOUBLE,

          temperature_min DOUBLE,
          temperature_max DOUBLE,
          temperature_afternoon DOUBLE,
          temperature_night DOUBLE,
          temperature_evening DOUBLE,
          temperature_morning DOUBLE,

          pressure_afternoon DOUBLE,

          wind_speed_max DOUBLE,
          wind_direction_max DOUBLE,

          PRIMARY KEY (lat, lon, date),
          INDEX idx_date (date),
          INDEX idx_loc (lat, lon)
        ) ENGINE=InnoDB;
        """
        self.cur.execute(sql)

    # -------------------------
    # 5) build backcast insert
    # -------------------------
    def build_backcast_insert_sql(self, data: dict):
        table = self.backcast_table

        sql = f"""
        INSERT IGNORE INTO {table} (
          lat, lon, tz, date, units,
          cloud_cover_afternoon, humidity_afternoon, precipitation_total,
          temperature_min, temperature_max, temperature_afternoon,
          temperature_night, temperature_evening, temperature_morning,
          pressure_afternoon,
          wind_speed_max, wind_direction_max
        ) VALUES (
          %s, %s, %s, %s, %s,
          %s, %s, %s,
          %s, %s, %s,
          %s, %s, %s,
          %s,
          %s, %s
        );
        """

        values = (
            data["lat"],
            data["lon"],
            data.get("tz"),
            data["date"],
            data.get("units"),

            data.get("cloud_cover", {}).get("afternoon"),
            data.get("humidity", {}).get("afternoon"),
            data.get("precipitation", {}).get("total"),

            data.get("temperature", {}).get("min"),
            data.get("temperature", {}).get("max"),
            data.get("temperature", {}).get("afternoon"),
            data.get("temperature", {}).get("night"),
            data.get("temperature", {}).get("evening"),
            data.get("temperature", {}).get("morning"),

            data.get("pressure", {}).get("afternoon"),

            data.get("wind", {}).get("max", {}).get("speed"),
            data.get("wind", {}).get("max", {}).get("direction"),
        )

        return sql, values

    # -------------------------
    # simple public API
    # -------------------------
    def insert_forecast(self, data: dict):
        sql, values = self.build_forecast_insert_sql(data)
        self.cur.execute(sql, values)

    def insert_backcast(self, data: dict):
        sql, values = self.build_backcast_insert_sql(data)
        self.cur.execute(sql, values)
