import { Injectable } from '@angular/core';
import { AngularFireDatabase} from '@angular/fire/database';

@Injectable({
  providedIn: 'root',
})
export class FirebaseService {

  constructor(private db: AngularFireDatabase) {
  }

  getConfig() {
    return this.db.list("webapp/config").query.once('value')
  }

  saveConfig(){
    return ""
  }
}