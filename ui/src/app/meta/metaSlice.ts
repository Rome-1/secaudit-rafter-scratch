/* eslint-disable @typescript-eslint/no-use-before-define */
import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { getConfig, getInfo } from '~/data/api';
import { IConfig, IInfo, StorageType } from '~/types/Meta';

export interface IMetaSlice {
  info: IInfo;
  config: IConfig;
  readonly: boolean;
}

const initialState: IMetaSlice = {
  info: {
    version: '0.0.0',
    latestVersion: '0.0.0',
    latestVersionURL: '',
    commit: '',
    buildDate: '',
    goVersion: '',
    updateAvailable: false,
    isRelease: false
  },
  config: {
    storage: {
      type: StorageType.DATABASE
    }
  },
  readonly: false
};

export const metaSlice = createSlice({
  name: 'meta',
  initialState,
  reducers: {},
  extraReducers(builder) {
    builder
      .addCase(fetchInfoAsync.fulfilled, (state, action) => {
        state.info = action.payload;
      })
      .addCase(fetchConfigAsync.fulfilled, (state, action) => {
        state.config = action.payload;
        // readonly source of truth is config.storage.readOnly when defined
        const storage = action.payload.storage;
        if (storage && typeof storage.readOnly === 'boolean') {
          state.readonly = storage.readOnly;
        } else {
          // default behavior when not defined
          state.readonly = storage?.type !== StorageType.DATABASE;
        }
      });
  }
});

export const selectInfo = (state: { meta: IMetaSlice }) => state.meta.info;
export const selectReadonly = (state: { meta: IMetaSlice }) =>
  state.meta.readonly;
// public selector to access full config
export const selectConfig = (state: { meta: IMetaSlice }): IConfig =>
  state.meta.config;

export const fetchInfoAsync = createAsyncThunk('meta/fetchInfo', async () => {
  const response = await getInfo();
  return response;
});

export const fetchConfigAsync = createAsyncThunk(
  'meta/fetchConfig',
  async () => {
    const response = await getConfig();
    return response;
  }
);

export default metaSlice.reducer;
