import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { UserInfo } from '../models/user-info'; // Adjust import path

@Injectable({
  providedIn: 'root'
})
export class SharedUserService {
  private _userInfo = new BehaviorSubject<UserInfo | null>(null);
  userInfo$ = this._userInfo.asObservable();

  setUserInfo(user: UserInfo) {
    this._userInfo.next(user);
  }

  getUserInfo(): UserInfo | null {
    return this._userInfo.value;
  }
}