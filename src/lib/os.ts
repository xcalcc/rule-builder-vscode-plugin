import * as os from 'os';

export const isWindows = (): boolean => {
    let osPlatform = os.platform().toString().toLowerCase();
    return osPlatform.indexOf('win') > -1;
}