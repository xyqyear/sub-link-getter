export interface GlobalConfig {
  openrouter_api_key: string;
  headless: boolean;
  solve_cloudflare: boolean;
  timeout: number;
  cache_file: string;
  browser_data_dir: string;
}

export interface SiteConfig {
  id: string;
  name: string;
  product_url: string;
  login_wait_selector: string;
  post_login_wait_selector: string;
  username_selector: string;
  password_selector: string;
  login_button_selector: string;
  captcha_image_selector: string | null;
  captcha_input_selector: string | null;
  captcha_retry_count: number;
  username: string;
  password: string;
  subscription_label_selector: string;
  subscription_group_selector: string;
  subscription_url_type: 'input' | 'copy';
  subscription_url_selector: string;
  subscription_url_attribute: string | null;
  subscription_name_pattern: string;
  subscription_url_retry_count: number;
  subscription_url_retry_delay_ms: number;
  content_validation: string;
}

export interface FetchSummaryResponse {
  name: string;
  url: string;
  content_length: number;
  cached: boolean;
}
