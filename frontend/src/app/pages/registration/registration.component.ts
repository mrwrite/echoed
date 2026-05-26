import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, FormControl, Validators, ReactiveFormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { Router, RouterModule } from '@angular/router';
import { RegisterDto } from '../../models/register-dto';
import { MetaService, EnumOption } from '../../services/meta.service';
import {
  normalizePendingOrganizationSetup,
  writePendingOrganizationSetup,
} from '../../shared/onboarding-flow';


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
  registrationSubmitted = false;

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
    this.registrationSubmitted = true;
    if (this.registrationForm.invalid) {
      this.registrationForm.markAllAsTouched();
      return;
    }

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
        const pendingSetup = normalizePendingOrganizationSetup({
          createOrganization: formValue.createOrganization,
          organizationName: formValue.organizationName,
          organizationType: this.inferredOrgTypeValue,
        });
        writePendingOrganizationSetup(pendingSetup);
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

  get createOrganizationSelected(): boolean {
    return !!this.registrationForm.get('createOrganization')?.value;
  }

  get organizationSetupSummary(): string {
    return this.createOrganizationSelected
      ? 'After you sign in, we will bring you directly into organization setup with your details prefilled.'
      : 'After you sign in, you can explore with your personal workspace and skip organization setup for now.';
  }

  get submitLabel(): string {
    return this.createOrganizationSelected ? 'Create account and continue to setup' : 'Create account';
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
