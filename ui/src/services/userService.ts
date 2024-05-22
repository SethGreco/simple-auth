import { config } from "../config/config"


export const checkToken = async (token: string): Promise<boolean> => {
    const url = `${config.backendUrl}/login/valid/`

    const response = await fetch(url, {
      method: 'GET',
      headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
      }
  })
  return await response.json()
}
