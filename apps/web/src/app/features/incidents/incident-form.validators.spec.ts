import { FormControl } from '@angular/forms';

import {
  localDateTimeMax,
  notFutureDateTime,
  trimmedLength,
} from './incident-form.validators';

function localDateTimeInput(date: Date): string {
  const offsetMs = date.getTimezoneOffset() * 60_000;
  return new Date(date.getTime() - offsetMs).toISOString().slice(0, 16);
}

describe('incident form validators', () => {
  it('validates useful length after trimming whitespace', () => {
    const control = new FormControl('  a  ', {
      nonNullable: true,
      validators: [trimmedLength(3, 120)],
    });

    expect(control.hasError('trimmedMinLength')).toBe(true);

    control.setValue('  WAN indisponível  ');
    expect(control.valid).toBe(true);
  });

  it('rejects a future incident start', () => {
    const future = localDateTimeInput(new Date(Date.now() + 60 * 60 * 1000));
    const control = new FormControl(future, {
      nonNullable: true,
      validators: [notFutureDateTime],
    });

    expect(control.hasError('futureDateTime')).toBe(true);
  });

  it('accepts a past incident start', () => {
    const past = localDateTimeInput(new Date(Date.now() - 60 * 60 * 1000));
    const control = new FormControl(past, {
      nonNullable: true,
      validators: [notFutureDateTime],
    });

    expect(control.valid).toBe(true);
  });

  it('formats the datetime-local maximum in local time', () => {
    const reference = new Date('2026-09-09T15:42:30-03:00');

    expect(localDateTimeMax(reference)).toBe('2026-09-09T15:42');
  });
});
