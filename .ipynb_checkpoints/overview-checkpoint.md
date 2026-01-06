项目目标:
- 美国国家公园的天气预报合订本; 
- 更好的拍照(瞬时)/更好的hike&backpack(多点位变化趋势)? 

数据类型:
- 天气预报（1-7天）;
- 实际天气;

数据来源:
- NOAA; --原始网格数据; 
- HRRR for visibility


数据内容:
- 时间:4 timestamp/day(sunrise,sunset,noon, midnight) 
- 数据点位:(NP + favourite locations)(Lat: °N, Lon: °W); 
- 数据频率:4 timestamp/day
- 气温（#）
- 天气类型,降雨量(#)，降雪量（#），降雨/雪概率（#），存雪量，云况雾况（skycover&visibility(only for spectifc NP)）， 风速(#)，湿度（#））

SQL格式：
时间：
0-sunrise
1-12:01pm（noon）
2-sunset
3-11:59pm
每个点位28+1个历史预测值（+实际值），每个预测值包含上述所有数据。
时间倒序排列，日出/日落时间做round
+HRRR

frontend：
现在的天气预报。（现场读取）

structure:
web

域名

技术路径:
- Python based AI coding ;
- LAMP : Linux, Apache2, Mysql, Python; 
