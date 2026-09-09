import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';

export function trimmedLength(min: number, max: number): ValidatorFn {
  return (control: AbstractControl<string>): ValidationErrors | null => {
    const value = control.value?.trim() ?? '';
    if (!value) return null;
    if (value.length < min) return { trimmedMinLength: { requiredLength: min, actualLength: value.length } };
    if (value.length > max) return { trimmedMaxLength: { requiredLength: max, actualLength: value.length } };
    return null;
  };
}

export function notFutureDateTime(control: AbstractControl<string>): ValidationErrors | null {
  const value = control.value;
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return { invalidDateTime: true };
  return date.getTime() > Date.now() ? { futureDateTime: true } : null;
}

export function localDateTimeMax(now = new Date()): string {
  const offsetMs = now.getTimezoneOffset() * 60_000;
  return new Date(now.getTime() - offsetMs).toISOString().slice(0, 16);
}
