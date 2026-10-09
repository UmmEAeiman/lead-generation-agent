export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
  };
}

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}
