项目目标:
- 美国国家公园的天气预报合订本; 
- 更好的拍照(瞬时)/更好的hike&backpack(多点位变化趋势)? 

数据类型:
- 天气预报（1-7天）;
- 实际天气;

数据来源:
- NOAA; --原始网格数据; 
- 国家公园观测站? 
- Openweather? 


数据内容:
- 时间, 天气; 
- 数据点位?  #每个公园多少个点位; 
- 数据频率?  #多久更新一次;
- 每天存储：4 timestamp/day(sunrise,sunset,noon, midnight) x (NP + favourite locations)(Lat: °N, Lon: °W) x100b (气温，天气类型,降雨量(#)，降雪量（#），降雨/雪概率（#），存雪量，云况雾况（skycover&visibility(only for spectifc NP)）， 风速(#)，湿度（#））


技术路径:
- Python based AI coding ;
- LAMP : Linux, Apache2, Mysql, Python; 
