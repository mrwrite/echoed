import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, FormControl, Validators, ReactiveFormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { Router, RouterModule } from '@angular/router';
import { RegisterDto } from '../../models/register-dto';
import { MetaService, EnumOption } from '../../services/meta.service';


@Component({
  selector: 'app-registration',
  standalone: true,
  imports: [CommonModule, RouterModule, ReactiveFormsModule],
  templateUrl: './registration.component.html',
  styleUrl: './registration.component.scss',
})
export class RegistrationComponent implements OnInit {
  registrationForm: FormGroup;
  errorMessage: string = '';
  showPassword = false;
  showConfirm = false;
  roleOptions: EnumOption[] = [];
  organizationTypes: EnumOption[] = [];
  loadingRoles = true;
  inferredOrgTypeLabel = '';
  inferredOrgTypeValue = '';
  showStudentOrgHint = false;

  constructor(
    private router: Router,
    private authService: AuthService,
    private fb: FormBuilder,
    private metaService: MetaService,
  ) {
    this.registrationForm = this.fb.group({
      password: new FormControl('', [
        Validators.required,
        Validators.minLength(6),
      ]),
      confirmPassword: new FormControl('', [Validators.required]),
      email: new FormControl('', [Validators.required, Validators.email]),
      firstName: new FormControl('', [Validators.required]),
      lastName: new FormControl('', [Validators.required]),
      role: new FormControl('', [Validators.required]),
      createOrganization: new FormControl(false),
      organizationName: new FormControl(''),
    });
  }

  ngOnInit(): void {
    this.registrationForm.valueChanges.subscribe(() =>
      this.checkPasswordMatch(),
    );

    this.metaService.getEnums().subscribe({
      next: (enums) => {
        console.log('Enums response:', enums);
        const allowed = new Set(['student', 'teacher', 'parent', 'instructor']);
        this.roleOptions = (enums.organizationRoles ?? []).filter((r) =>
          allowed.has(r.value),
        );
        this.organizationTypes = enums.organizationTypes ?? [];
        this.updateInferredOrgType();
        this.loadingRoles = false;
      },
      error: (err) => {
        console.error('Enums load failed (even if status=200):', err);
        this.roleOptions = [
          { key: 'STUDENT', value: 'student', label: 'Student' },
          { key: 'TEACHER', value: 'teacher', label: 'Teacher' },
        ];
        this.loadingRoles = false;
      },
    });

    this.registrationForm.get('role')?.valueChanges.subscribe(() => {
      this.updateInferredOrgType();
    });

    this.registrationForm.get('createOrganization')?.valueChanges.subscribe((enabled) => {
      const orgNameControl = this.registrationForm.get('organizationName');
      if (enabled) {
        orgNameControl?.setValidators([Validators.required]);
      } else {
        orgNameControl?.clearValidators();
        orgNameControl?.setValue('');
      }
      orgNameControl?.updateValueAndValidity();
    });
    
  }

  checkPasswordMatch() {
    const password = this.registrationForm.get('password')?.value;
    const confirmPassword = this.registrationForm.get('confirmPassword')?.value;

    if (password && confirmPassword && password !== confirmPassword) {
      this.registrationForm
        .get('confirmPassword')
        ?.setErrors({ passwordMismatch: true });
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
        if (formValue.createOrganization && formValue.organizationName) {
          const payload = {
            name: formValue.organizationName,
            type: this.inferredOrgTypeValue,
          };
          sessionStorage.setItem('pending_org_creation', JSON.stringify(payload));
        } else {
          sessionStorage.removeItem('pending_org_creation');
        }
        this.router.navigate(['/login']);
      },
      (error) => {
        console.log('Registration failed');
        this.errorMessage =
          error?.error?.detail ||
          'Registration failed. Please check your details and try again.';
      },
    );
  }

  private updateInferredOrgType(): void {
    const role = this.registrationForm.get('role')?.value;
    const inferredType = this.getOrgTypeForRole(role);
    this.inferredOrgTypeValue = inferredType;
    const match = this.organizationTypes.find((t) => t.value === inferredType);
    this.inferredOrgTypeLabel = match?.label ?? inferredType;
    this.showStudentOrgHint = role === 'student';
  }

  private getOrgTypeForRole(role: string): string {
    switch (role) {
      case 'parent':
        return 'family';
      case 'teacher':
      case 'instructor':
        return 'school';
      case 'student':
        return 'family';
      default:
        return 'personal';
    }
  }
}
