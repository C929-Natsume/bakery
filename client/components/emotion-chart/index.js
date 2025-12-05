// components/emotion-chart/index.js
Component({
  properties: {
    chartData: {
      type: Object,
      observer: function(newVal) {
        if (newVal) {
          this.renderChart()
        }
      }
    },
    type: {
      type: String,
      value: 'distribution' // 'distribution' 或 'trend'
    }
  },

  data: {
    ec: {
      lazyLoad: true
    },
    chart: null
  },

  lifetimes: {
    attached() {
      this.initChart()
    },
    detached() {
      if (this.chart) {
        this.chart.dispose()
      }
    }
  },

  methods: {
    initChart() {
      this.ecComponent = this.selectComponent('#emotion-chart')
      this.renderChart()
    },

    renderChart() {
      if (!this.ecComponent || !this.properties.chartData) {
        return
      }

      this.ecComponent.init((canvas, width, height, dpr) => {
        const chart = echarts.init(canvas, null, {
          width: width,
          height: height,
          devicePixelRatio: dpr
        })

        const option = this.getChartOption()
        chart.setOption(option)
        this.chart = chart
        return chart
      })
    },

    getChartOption() {
      if (this.properties.type === 'distribution') {
        return this.getPieChartOption()
      } else {
        return this.getLineChartOption()
      }
    },

    getPieChartOption() {
      const distribution = this.properties.chartData.distribution || []
      const pieData = distribution.map(item => ({
        name: item.emotion_label?.name || '未知情绪',
        value: item.count || 0,
        itemStyle: {
          color: item.emotion_label?.color || this.getRandomColor()
        }
      })).filter(item => item.value > 0)

      return {
        title: {
          text: '情绪分布统计',
          left: 'center',
          top: 20,
          textStyle: {
            color: '#5A4C3E',
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c}次 ({d}%)'
        },
        legend: {
          orient: 'horizontal',
          left: 'center',
          bottom: 20,
          textStyle: {
            color: '#8B7355'
          }
        },
        series: [{
          name: '情绪分布',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: true,
          itemStyle: {
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: true,
            formatter: '{b}: {c}次'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 14,
              fontWeight: 'bold'
            }
          },
          data: pieData
        }]
      }
    },

    getLineChartOption() {
      const trend = this.properties.chartData.trend || {}
      const dates = Object.keys(trend).sort()
      const emotionLabels = new Set()
      
      // 收集所有情绪标签
      dates.forEach(date => {
        const emotions = trend[date] || []
        emotions.forEach(emotion => {
          if (emotion.emotion_label?.name) {
            emotionLabels.add(emotion.emotion_label.name)
          }
        })
      })

      // 为每个情绪标签创建数据系列
      const series = Array.from(emotionLabels).map(label => {
        const data = dates.map(date => {
          const emotions = trend[date] || []
          const emotion = emotions.find(e => e.emotion_label?.name === label)
          return emotion ? emotion.count : 0
        })

        return {
          name: label,
          type: 'line',
          smooth: true,
          symbol: 'circle',
          symbolSize: 8,
          data: data
        }
      })

      return {
        title: {
          text: '情绪趋势图',
          left: 'center',
          top: 20,
          textStyle: {
            color: '#5A4C3E',
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'axis',
          formatter: function(params) {
            let result = params[0].axisValue + '<br/>'
            params.forEach(param => {
              result += param.marker + param.seriesName + ': ' + param.value + '次<br/>'
            })
            return result
          }
        },
        legend: {
          data: Array.from(emotionLabels),
          orient: 'horizontal',
          left: 'center',
          bottom: 20,
          textStyle: {
            color: '#8B7355'
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          top: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: dates,
          axisLine: {
            lineStyle: {
              color: '#8B7355'
            }
          },
          axisLabel: {
            color: '#8B7355',
            fontSize: 12,
            formatter: function(value) {
              return value.substring(5) // 只显示月-日
            }
          }
        },
        yAxis: {
          type: 'value',
          axisLine: {
            lineStyle: {
              color: '#8B7355'
            }
          },
          axisLabel: {
            color: '#8B7355',
            fontSize: 12
          },
          splitLine: {
            lineStyle: {
              color: ['#FFD8A6'],
              type: 'dashed'
            }
          }
        },
        series: series
      }
    },

    getRandomColor() {
      const colors = ['#FF9A76', '#FFD47F', '#A8E6CF', '#78C2FF', '#B19CFF', '#FFB7D5']
      return colors[Math.floor(Math.random() * colors.length)]
    }
  }
})