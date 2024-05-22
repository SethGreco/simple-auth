import { redirect } from "react-router-dom";
import * as authMock from './authService';


jest.mock("../config/config", () => ({
    config: {
        backendUrl: "http://localhost:8000",
    },
  }));

describe('getAuthToken', () => {
    test('returns token when it is present in localStorage', () => {
        const token = 'dummytoken';
        jest.spyOn(Storage.prototype, 'getItem').mockReturnValueOnce(token);

        expect(authMock.getAuthToken()).toBe(token);
        expect(localStorage.getItem).toHaveBeenCalledWith('token');
    })

    test('returns null when token is not present in localStorage', () => {
        jest.spyOn(Storage.prototype, 'getItem').mockReturnValueOnce(null);

        expect(authMock.getAuthToken()).toBeNull();
        expect(localStorage.getItem).toHaveBeenCalledWith('token');
    })
})


jest.mock('react-router-dom', () => ({
    redirect: jest.fn()
}))

describe('isAuthenticated', () => {
    test('returns token when present', () => {
        const mock = jest.spyOn(authMock, 'getAuthToken');
        mock.mockImplementation(() => 'dummyToken');
        const result = authMock.isAuthenticated();
        expect(result).toBe('dummyToken');
        expect(authMock.getAuthToken).toHaveBeenCalled();
        expect(redirect).not.toHaveBeenCalled();
    });
    test('returns redirect when token not present', () => {
        const mock = jest.spyOn(authMock, 'getAuthToken');
        mock.mockImplementation(() => null);
        authMock.isAuthenticated();
        expect(redirect).toHaveBeenCalled();
    });
})
