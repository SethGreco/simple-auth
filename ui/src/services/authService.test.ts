// import { redirect } from "react-router-dom";
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
        jest.spyOn(Storage.prototype, 'getItem').mockReturnValueOnce('token');

        expect(authMock.getAuthToken()).toBeNull();
        expect(localStorage.getItem).toHaveBeenCalledWith('token');
    })
})


// jest.mock('react-router-dom', () => ({
//     redirect: jest.fn()
// }))