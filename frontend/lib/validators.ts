export interface FieldRule {
  validate: (value: string) => string | null;
}

export const required = (label: string): FieldRule => ({
  validate: (value) => (value.trim() ? null : `${label} is required.`),
});

export const emailRule: FieldRule = {
  validate: (value) =>
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim())
      ? null
      : "Enter a valid email address.",
};

export const minLength = (label: string, min: number): FieldRule => ({
  validate: (value) =>
    value.trim().length >= min ? null : `${label} must be at least ${min} characters.`,
});

export const optionalUrl: FieldRule = {
  validate: (value) =>
    !value.trim() || /^https?:\/\/\S+\.\S+/.test(value.trim())
      ? null
      : "Enter a valid URL (https://…).",
};

export function runRules(value: string, rules: FieldRule[]): string | null {
  for (const rule of rules) {
    const error = rule.validate(value);
    if (error) return error;
  }
  return null;
}
