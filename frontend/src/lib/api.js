const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

export async function request(endpoint, method = 'GET', body = null) {
  const headers = {
    'Content-Type': 'application/json',
  };

  const token = localStorage.getItem('access_token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config = {
    method,
    headers,
  };

  if (body) {
    config.body = JSON.stringify(body);
  }

  try {
    const response = await fetch(`${API_URL}${endpoint}`, config);
    const data = await response.json();

    if (!response.ok) {
      throw new ApiError(data.detail || `Error del servidor (${response.status})`, response.status);
    }
    
    return data;
  } catch (error) {
    // ENMASCARAR URL EN MENSAJES DE ERROR PARA SEGURIDAD
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      console.error("Error de conexión: Revisa tu conexión a internet", error);
    } else if (error instanceof ApiError) {
      console.error(`Error API ${error.status}: ${error.message}`, error);
    } else {
      console.error("Error inesperado en la aplicación", error);
    }
    throw error;
  }
}

export const api = {
  // Auth
  login: (username, password) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    
    return fetch(`${API_URL}/token`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData
    }).then(async res => {
        if (!res.ok) throw new Error('Error en el inicio de sesión');
        return res.json();
    }).catch(error => {
      console.error("Error de autenticación", error);
      throw error;
    });
  },
  register: (user) => request('/usuarios', 'POST', user),

  // Dashboard
  getDashboard: () => request('/dashboard'),
  
  // Movimientos
  getMovimientos: () => request('/movimientos'),
  createMovimiento: (data) => request('/movimientos', 'POST', data),
  updateMovimiento: (id, data) => request(`/movimientos/${id}`, 'PUT', data),
  deleteMovimiento: (id) => request(`/movimientos/${id}`, 'DELETE'),

  // Cuentas
  getCuentas: () => request('/cuentas'),
  createCuenta: (data) => request('/cuentas', 'POST', data),
  deleteCuenta: (id) => request(`/cuentas/${id}`, 'DELETE'),
  
  // Categorias
  getCategorias: () => request('/categorias'),
  createCategoria: (data) => request('/categorias', 'POST', data),
  deleteCategoria: (id) => request(`/categorias/${id}`, 'DELETE'),

  // Metas
  getMetas: () => request('/metas'),
  createMeta: (data) => request('/metas', 'POST', data),
  abonarMeta: (metaId, data) => request(`/metas/${metaId}/abonar`, 'POST', data),
  updateMeta: (id, data) => request(`/metas/${id}`, 'PUT', data),
  deleteMeta: (id) => request(`/metas/${id}`, 'DELETE'),

  // Usuarios (Perfil)
  getProfile: () => request('/usuarios/me'),
  updateProfile: (data) => request('/usuarios/me', 'PUT', data),
  changePassword: (data) => request('/usuarios/cambiar-password', 'PUT', data),
};
