import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { MatSnackBar } from '@angular/material/snack-bar';
import { FormControl, FormGroupDirective, NgForm, Validators } from '@angular/forms';
import { ErrorStateMatcher } from '@angular/material/core';

const NOTION_SERVER_ENDPOINT = 'https://026eee0dacbf.ap.ngrok.io/';

export class MyErrorStateMatcher implements ErrorStateMatcher {
  isErrorState(control: FormControl | null, form: FormGroupDirective | NgForm | null): boolean {
    const isSubmitted = form && form.submitted;
    return !!(control && control.invalid && (control.dirty || control.touched || isSubmitted));
  }
}

@Component({
  selector: 'app-ns',
  templateUrl: './ns.component.html',
  styleUrls: ['./ns.component.css']
})
export class NsComponent implements OnInit {
  daysToOrd = 0
  loading = false;
  detail = {"veh_type":"","veh_mid":"","veh_avi":"","veh_fe":""}

  detailSourceFormControl = new FormControl('', [Validators.required]);
  detailTitleFormControl = new FormControl('', [Validators.required]);

  matcher = new MyErrorStateMatcher();

  constructor(private _snackBar: MatSnackBar, private http: HttpClient) { }

  ngOnInit() {
    var ord = new Date("2021-08-15"); 
    var today = new Date();
    this.daysToOrd = Math.round((ord.getTime() - today.getTime()) / (24*60*60*1000))
  }

  submitToNotion() {
    if (this.detailSourceFormControl.value != "" && !this.loading) {
      this.loading = true
      this.detailSourceFormControl.disable()

      this.http.post(NOTION_SERVER_ENDPOINT + "insertDetailToNotion/", this.detailSourceFormControl.value)
        .subscribe(
          (val) => {
            let msg = ""
            msg = val["status"] + ": "
            val["detail"].forEach(item => {
              msg += " " + item[1]
            });
            msg += " created"
            this._snackBar.open(msg, "", {
              duration: 5000,
            });
            this.detailSourceFormControl.reset()
            this.detailSourceFormControl.enable()
            this.loading = false;
          });
    }
  }

  getDetailTemplate(){
    if (this.detailTitleFormControl.value != "" && !this.loading) {
      this.http.get(NOTION_SERVER_ENDPOINT + "getDetailTemplate/" + this.detailTitleFormControl.value )
        .subscribe(
          (val) => {
            if (val["data"] != "") {
              this.detail = val["data"]
            }else{
              this._snackBar.open(val["msg"], "", {
                duration: 5000,
              });
            }
          });
    }
  }
}
