import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';

// Service
import { MainSocketService } from '../../../core/services/main.socket.service';

// Model
import { MainEvent } from '../../../data/client-enums';
import { TaskConfig } from '../../../data/taskConfig.model';

// Plot
import { PlotType as type } from '../../../data/client-enums';
import { Color as colors } from '../../../data/client-enums';
import { Smooth as smooth } from '../../../data/client-enums';

import { Solution } from '../../../data/taskData.model';


@Component({
  selector: 'hm-reg',
  templateUrl: './heat-map-reg.component.html',
  styleUrls: ['./heat-map-reg.component.scss']
})
export class HeatMapRegComponent implements OnInit {

  // Variables
  prediction = new Map()
  solution: Solution
  measPoints: Array<Array<number>> = []
  
  resetRes() {
    this.prediction.clear()
    this.solution = undefined
    this.measPoints = []
  }

  @ViewChild('reg') reg: ElementRef;

  globalConfig: object
  taskConfig: TaskConfig
  // Rendering axises
  y: Array<number>
  x: Array<number>

  // Default theme
  theme = {
    type: type[0],
    color: colors[0],
    smooth: smooth[0]
  }
  public type = type
  public colors = colors
  public smooth = smooth

  constructor(private ioMain: MainSocketService) { }

  ngOnInit() {
    this.initMainConnection();
    // window.onresize = () => Plotly.relayout(this.reg.nativeElement, {})
  }

  isModelType(type: String) {
    return this.taskConfig && this.taskConfig.ModelConfiguration.ModelType == type
  }

  // Rendering
  regrRender(): void {
    let regression = this.reg.nativeElement
    const data = [
      {
        z: this.zParser(this.prediction),
        x: this.x,
        y: this.y,
        type: this.theme.type,
        colorscale: this.theme.color,
        zsmooth: this.theme.smooth
      },
      {
        type: 'scatter',
        mode: 'markers',
        name: 'measured points',
        marker: { color: 'grey', size: 8, symbol: 'x' },
        x: this.measPoints.map(arr => arr[1]),
        y: this.measPoints.map(arr => arr[0]) 
      },
      {
        type: 'scatter',
        mode: 'markers',
        name: 'solution',
        marker: { color: 'Gold', size: 16, symbol: 'star' },
        x: this.solution && [this.solution.configurations[1]],
        y: this.solution && [this.solution.configurations[0]]
      }
    ];

    var layout = {
      title: 'Regression',
      autosize: true,
      showlegend: false,
      xaxis: { title: "Threads",
        type: 'category',
        autorange: true,
        range: [Math.min(...this.x), Math.max(...this.x)] 
      },
      yaxis: { title: "Frequency",
        type: 'category',
        autorange: true,
        range: [Math.min(...this.y), Math.max(...this.y)]  }
    };

    Plotly.react(regression, data, layout);
  }
  zParser(data: Map<String, Number>): Array<Array<Number>> {
    var z = []
    this.y.forEach(y => { // y - threads
      var row = []
      this.x.forEach(x => { // x - frequency
        row.push(data.get(String([y, x]))[0]) // change [x,y] or [y,x] if require horizontal or vertical orientation
                                          // Get the first result from an array
      });
      z.push(row)
    });
    return z
  }

  // Init conection
  private initMainConnection(): void {

    this.ioMain.onEmptyEvent(MainEvent.CONNECT)
      .subscribe(() => {
        console.log(' regresion: connected');
      });
    this.ioMain.onEmptyEvent(MainEvent.DISCONNECT)
      .subscribe(() => {
        console.log(' regresion disconnected');
      });
    // ---- Main events

    this.ioMain.onEvent(MainEvent.FINAL) //// ???
      .subscribe((obj: any) => {
        obj["task"] && obj["task"].forEach(result => {
          if (result) {
            this.solution = result // In case if only one point solution
          } else {
            console.log("Empty solution")
          }
          this.measPoints.push(result['configurations'])
          // this.measPoints = result['measured points']
        })
        console.log("Measured", this.measPoints.length)
        this.prediction.size && this.regrRender()
      });

    this.ioMain.onEvent(MainEvent.EXPERIMENT)
      .subscribe((obj: any) => {
        this.globalConfig = obj['configuration']['global configuration']
        this.taskConfig = obj['configuration']['experiment configuration']
        this.y = this.taskConfig['DomainDescription']['AllConfigurations'][0] // frequency
        this.x = this.taskConfig['DomainDescription']['AllConfigurations'][1] // threads
        this.resetRes() // Clear the old data and results
      });

    this.ioMain.onEvent(MainEvent.PREDICTIONS)
      .subscribe((obj: any) => {
        obj["task"] && obj["task"].forEach(point => {
          if (point) {
            this.prediction.set(String(point['configurations']), point['results'])
          } else {
            console.log("Empty prediction point")
          }
        })
        console.log(" Regresion points:", obj['task'].length)
        this.prediction.size && this.regrRender()
      });

  }

}
