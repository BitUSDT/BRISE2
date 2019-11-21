import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';

// Service
import { MainSocketService } from '../../../core/services/main.socket.service';

import { Solution } from '../../../data/taskData.model';
import { MainEvent } from '../../../data/client-enums';

import { ExperimentDescription } from '../../../data/experimentDescription.model';

interface PointExp {
  configurations: Array<any>;
  results: Array<any>;
  time: any;
  'measured points': number;
} 

@Component({
  selector: 'imp-res',
  templateUrl: './imp-res.component.html',
  styleUrls: ['./imp-res.component.scss']
})
export class ImpResComponent implements OnInit {
  // The experiments results
  bestRes = new Set<PointExp>()
  allRes = new Set<PointExp>()
  // Best point 
  solution: Solution

  experimentDescription: ExperimentDescription

  // poiner to DOM element #map
  @ViewChild('improvement') impr: ElementRef;

  constructor(private ioMain: MainSocketService) { }

  ngOnInit() {
    this.initMainEvents();
    window.onresize = () => this.bestRes.size>2 && this.render()
  }
  //                              WebSocket
  // --------------------------   Main-node
  private initMainEvents(): void {
    this.ioMain.onEvent(MainEvent.EXPERIMENT)
      .subscribe((obj: any) => {
        this.experimentDescription = obj['description']['experiment description']
      });

    this.ioMain.onEvent(MainEvent.FINAL)
      .subscribe((obj: any) => {
        obj["configuration"] && obj["configuration"].forEach(configuration => {
          this.solution = configuration
          let min = new Date().getMinutes()
          let sec = new Date().getSeconds()
          let temp: PointExp = {
            'configurations': configuration['configurations'],
            'results': configuration['results'],
            'time': min + 'm ' + sec + 's',
            'measured points': configuration['measured points']
          }
          this.allRes.add(temp)
          this.bestRes.add(temp) // There is no check if this solution is the best decision 
        })
        this.render() // Render chart when all points got
      });

      this.ioMain.onEvent(MainEvent.DEFAULT).subscribe((obj: any) => {
        obj["configuration"] && obj["configuration"].forEach(configuration => {
          this.solution = configuration
          let min = new Date().getMinutes()
          let sec = new Date().getSeconds()
          let temp: PointExp = {
            'configurations': configuration['configurations'],
            'results': configuration['results'],
            'time': min + 'm ' + sec + 's',
            'measured points': this.allRes.size + 1
          }
          this.allRes.add(temp)
          this.bestRes.add(temp) // There is no check if this solution is the best decision 
        })
        this.render() // Render chart when all points got         
    });

    this.ioMain.onEvent(MainEvent.NEW)
      .subscribe((obj: any) => {
        obj["configuration"] && obj["configuration"].forEach(configuration => {
          let min = new Date().getMinutes()
          let sec = new Date().getSeconds()
          this.allRes.add({
            'configurations': configuration['configurations'],
            'results': configuration['results'],
            'time': min + 'm ' + sec + 's',
            'measured points': this.allRes.size + 1
          }) // Add new point(result)
          let temp: PointExp = {
            'configurations': configuration['configurations'],
            'results': configuration['results'],
            'time': min + 'm ' + sec + 's',
            'measured points': this.allRes.size
          }

          // Check the best available point
          this.bestRes && this.bestRes.forEach(function (resItem) {
            // TODO: Max or min from task
            if (temp.results[0] > resItem.results[0]) { // check FIRST result from array!
              temp.results = resItem.results
              temp.configurations = resItem.configurations
            }
          })
          this.bestRes.add(temp) // Add the best available point(result)
        })
        this.bestRes.size>2 && this.render()
      });

    this.ioMain.onEvent(MainEvent.EXPERIMENT)
      .subscribe((obj: any) => {
        if (obj["configuration"]) {
          this.bestRes.clear()
          this.allRes.clear()
          this.solution = undefined
        }
      });
  }

  render() {
    // DOM element. Render point
    const element = this.impr.nativeElement

    // X-axis data
    const xBest = Array.from(this.bestRes).map(i => i["measured points"]);
    // Results
    const yBest = Array.from(this.bestRes).map(i => i["results"][0]);
    
    var allResultSet = { // Data for all results
      x: Array.from(this.allRes).map(i => i["measured points"]),
      y: Array.from(this.allRes).map(i => i["results"][0]),
      type: 'scatter',
      mode: 'lines+markers',
      line: { color: 'rgba(67,67,67,1)', width: 1, shape: 'spline', dash: 'dot' },
      text: Array.from(this.allRes).map(i => String(i["configurations"])),
      marker: {
        color: 'rgba(255,64,129,1)',
        size: 8,
        symbol: 'x'
      },
      name: 'results'
    }
    var bestPointSet = { // Data for the best available results 
      x: xBest,
      y: yBest,
      type: 'scatter',
      mode: 'lines+markers',
      line: { color: 'rgba(67,67,67,1)', width: 2, shape: 'spline' },
      name: 'best point',
      marker: { size: 6, symbol: 'x', color: 'rgba(67,67,67,1)' }
    }

    var startEndPoint = { // Start & Finish markers
      x: [xBest[0], xBest[xBest.length - 1]],
      y: [yBest[0], yBest[yBest.length - 1]],
      type: 'scatter',
      mode: 'markers',
      hoverinfo: 'none',
      showlegend: false,
      marker: { color: 'rgba(255,64,129,1)', size: 10 }
    }

    let data = [allResultSet, bestPointSet, startEndPoint];

    var layout = {
      title: 'The best results',
      showlegend: true,
      autosize: true,
      xaxis: {
        title: "Sequence number",
        showline: true,
        showgrid: false,
        zeroline: false,
        showticklabels: true,
        linecolor: 'rgb(204,204,204)',
        linewidth: 2,
        autotick: false,
        ticks: 'outside',
        tickcolor: 'rgb(204,204,204)',
        tickwidth: 2,
        ticklen: 5,
        tickfont: {
          family: 'Roboto',
          size: 12,
          color: 'rgb(82, 82, 82)'
        }
      },
      yaxis: {
        title: this.experimentDescription["TaskConfiguration"]["ResultStructure"][0],
        showgrid: false,
        zeroline: false,
        showline: true,
        linecolor: 'rgb(204,204,204)',
        showticklabels: true,
        ticks: 'outside',
        tickcolor: 'rgb(204,204,204)',
        ticklen: 5,
        tickfont: {
          family: 'Roboto',
          size: 12,
          color: 'rgb(82, 82, 82)'
        }
      },
    };

    Plotly.react(element, data, layout);
  }

}
