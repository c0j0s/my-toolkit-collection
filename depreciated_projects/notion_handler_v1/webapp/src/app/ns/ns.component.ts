import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { MatSnackBar } from '@angular/material/snack-bar';
import { FormControl, FormGroupDirective, NgForm, Validators } from '@angular/forms';
import { ErrorStateMatcher } from '@angular/material/core';
import { FirebaseService } from '../services/firebase.service'

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
  notion_endpoints;
  daysToOrd = 0;
  loading = true;
  detail = {"veh_type":"","veh_mid":"","veh_avi":"","veh_fe":"","poc":"","poc_contact_no":""}

  detailSourceFormControl = new FormControl('', [Validators.required]);
  detailTitleFormControl = new FormControl('', [Validators.required]);

  matcher = new MyErrorStateMatcher();

  constructor(private firebaseService:FirebaseService, private _snackBar: MatSnackBar, private http: HttpClient) { }

  ngOnInit() {
    this.firebaseService.getConfig().then(snapshot => {
      this.notion_endpoints = snapshot.child("endpoint").val()
      this.daysToOrd = Math.round((new Date(snapshot.child("ord_countdown/ord_date").val().toString()).getTime() - new Date().getTime()) / (24*60*60*1000))
      this.loading = false
    });
  }

  submitToNotion() {
    if (this.detailSourceFormControl.value != "" && !this.loading) {
      this.loading = true
      this.detailSourceFormControl.disable()

      this.http.post(this.notion_endpoints["notion_server"] + this.notion_endpoints["insert_detail_to_notion"], this.detailSourceFormControl.value)
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
      this.http.get(this.notion_endpoints["notion_server"] + this.notion_endpoints["detail_report_template"] + this.detailTitleFormControl.value )
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
