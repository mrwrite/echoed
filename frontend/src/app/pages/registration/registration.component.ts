import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, FormControl, Validators, ReactiveFormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { Router, RouterModule } from '@angular/router';
import { RegisterDto } from '../../models/register-dto';


@Component({
  selector: 'app-registration',
  standalone: true,
  imports: [ CommonModule, RouterModule, ReactiveFormsModule ],
  templateUrl: './registration.component.html',
  styleUrl: './registration.component.scss'
})
export class RegistrationComponent implements OnInit{
  registrationForm: FormGroup;
  errorMessage: string = '';
  showPassword = false;
  showConfirm = false;

  constructor(private router: Router, private authService: AuthService, private fb: FormBuilder) {
    this.registrationForm = this.fb.group({      
      password: new FormControl('', [Validators.required, Validators.minLength(6)]),
      confirmPassword: new FormControl('', [Validators.required]),
      email: new FormControl('', [Validators.required, Validators.email]),
      firstName: new FormControl('', [Validators.required]),
      lastName: new FormControl('', [Validators.required]),
      role: new FormControl('', [Validators.required]),
    });
   }

   ngOnInit(): void {
     this.registrationForm.valueChanges.subscribe(() => this.checkPasswordMatch());
   }

   checkPasswordMatch() {
      const password = this.registrationForm.get('password')?.value;
      const confirmPassword = this.registrationForm.get('confirmPassword')?.value;

      if (password && confirmPassword && password !== confirmPassword) {
        this.registrationForm.get('confirmPassword')?.setErrors({ passwordMismatch: true });
      } else {
        this.registrationForm.get('confirmPassword')?.setErrors(null);
      }
   }

   onSubmit(): void {
    if (this.registrationForm.invalid) return;

    const formValue = this.registrationForm.value;
    const user: RegisterDto = {
      username: formValue.email,
      password: formValue.password,
      email: formValue.email,
      firstname: formValue.firstName,
      lastname: formValue.lastName,
      role: formValue.role,
    };

    this.authService.register(user).subscribe(
      (response) => {
        console.log('Registration successful');
        this.router.navigate(['/login']);
      },
      (error) => {
        console.log('Registration failed');
        this.errorMessage = error?.error?.detail || 'Registration failed. Please check your details and try again.';
      }
    );
   }

}
