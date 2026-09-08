import { provideRouter } from '@angular/router';
import { TestBed } from '@angular/core/testing';

import { AppComponent } from './app.component';

describe('AppComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AppComponent],
      providers: [provideRouter([])],
    }).compileComponents();
  });

  it('renders the product identity and main landmark', () => {
    const fixture = TestBed.createComponent(AppComponent);
    fixture.detectChanges();

    const element = fixture.nativeElement as HTMLElement;

    expect(element.querySelector('header')?.textContent).toContain(
      'NOC Flow Cloud v2',
    );
    expect(element.querySelector('main#main-content')).not.toBeNull();
    expect(element.querySelector('.skip-link')?.getAttribute('href')).toBe(
      '#main-content',
    );
  });
});
