import { getApiBaseUrl } from '../apiConfig';

export interface AuthTokenResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  name: string;
  email: string;
  role: string;
}

export interface UserProfileResponse {
  id: number;
  name: string;
  email: string;
  phone?: string | null;
  role: string;
  created_at: string;
}

export interface SafetyProfileData {
  emergencyContactName: string;
  emergencyContactPhone: string;
  preferredLanguage: 'te' | 'en' | 'hi';
  locationGranted: boolean;
}

class AuthService {
  private get baseUrl(): string {
    return `${getApiBaseUrl()}/api/v1/auth`;
  }

  /**
   * Authenticate user with Email or Phone and Password
   */
  async login(emailOrPhone: string, password: string): Promise<AuthTokenResponse> {
    const response = await fetch(`${this.baseUrl}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        email: emailOrPhone.trim(),
        password: password,
      }),
    });

    if (!response.ok) {
      let errorMsg = 'The email/phone or password entered is incorrect.';
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMsg = typeof errorData.detail === 'string' ? errorData.detail : errorData.detail[0]?.msg || errorMsg;
        } else if (errorData.message) {
          errorMsg = errorData.message;
        } else if (errorData.error?.message) {
          errorMsg = errorData.error.message;
        }
      } catch {
        // Use default errorMsg
      }
      throw new Error(errorMsg);
    }

    const data: AuthTokenResponse = await response.json();
    return data;
  }

  /**
   * Register a new Citizen account
   */
  async register(
    name: string,
    emailOrPhone: string,
    password: string,
    phone?: string
  ): Promise<AuthTokenResponse> {
    // If user provided a phone in the identifier and email in separate, normalize
    const isEmail = emailOrPhone.includes('@');
    const email = isEmail ? emailOrPhone.trim().toLowerCase() : `${emailOrPhone.replace(/\D/g, '')}@citizen.disasterguard.gov`;
    const userPhone = phone || (!isEmail ? emailOrPhone.trim() : undefined);

    const response = await fetch(`${this.baseUrl}/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        name: name.trim(),
        email: email,
        phone: userPhone,
        password: password,
        role: 'CITIZEN',
      }),
    });

    if (!response.ok) {
      let errorMsg = 'Failed to create emergency protection account.';
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMsg = typeof errorData.detail === 'string' ? errorData.detail : errorData.detail[0]?.msg || errorMsg;
        } else if (errorData.message) {
          errorMsg = errorData.message;
        } else if (errorData.error?.message) {
          errorMsg = errorData.error.message;
        }
      } catch {
        // Use default errorMsg
      }
      throw new Error(errorMsg);
    }

    const data: AuthTokenResponse = await response.json();
    return data;
  }

  /**
   * Fetch current authenticated citizen profile
   */
  async getCurrentUser(token: string): Promise<UserProfileResponse> {
    const response = await fetch(`${this.baseUrl}/me`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Session expired. Please log in again.');
    }

    const data: UserProfileResponse = await response.json();
    return data;
  }
}

export const authService = new AuthService();
