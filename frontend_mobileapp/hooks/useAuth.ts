import { useEffect, useState } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { jwtDecode } from "jwt-decode";

interface DecodedToken {
  sub: number; // user_id
  exp: number; // expiry timestamp
  iat: number; // issued at timestamp
  [key: string]: any; // allow extra fields just in case
}

interface AuthState {
  token: string | null;
  userId: number | null;
  isAuthenticated: boolean;
  loading: boolean;
}

export function useAuth(): AuthState {
  const [token, setToken] = useState<string | null>(null);
  const [userId, setUserId] = useState<number | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchToken = async () => {
      try {
        const storedToken = await AsyncStorage.getItem("token");
        if (storedToken) {
          setToken(storedToken);
          const decoded = jwtDecode<DecodedToken>(storedToken);
          setUserId(decoded.sub);
        }
      } catch (error) {
        console.error("Failed to decode or fetch token:", error);
        setToken(null);
        setUserId(null);
      } finally {
        setLoading(false);
      }
    };

    fetchToken();
  }, []);

  return {
    token,
    userId,
    isAuthenticated: token !== null && userId !== null,
    loading,
  };
}
