export const HTTP_UNPROCESSABLE_ENTITY = 422
export const HTTP_NOT_FOUND = 404
export const HTTP_FORBIDDEN = 403
export const HTTP_OK = 200
export const HTTP_NO_CONTENT = 204

/**
 * @param {RequestInfo} url
 * @param params
 * @return {Promise<Object>}
 */
export async function jsonFetch(url, csrf, params = {}) {
    // Si on reçoit un FormData on le convertit en objet

    if (params.body instanceof FormData) {
        params.body = Object.fromEntries(params.body)
    }

    if (params.body && typeof params.body === 'object') {
        params.body = JSON.stringify(params.body)
    }

    params = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Accept: 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrf
        },
        ...params
    }

    const response = await fetch(url, params)
    if (response.status === 204) {
        return null
    }

    const data = await response.json()
    if (response.ok) {
        return data
    }

    console.log({data})

    throw new ApiError(data, response.status)
}


/**
 * Représente une erreur d'API
 * @property {{
 *  violations: {propertyPath: string, message: string}
 * }} data
 */
export class ApiError {
    constructor(data, status) {
        this.data = data
        this.status = status
    }
}
