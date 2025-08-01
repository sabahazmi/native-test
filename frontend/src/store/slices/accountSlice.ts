import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface Account {
  id: number;
  account_number: string;
  name: string;
  account_type: string;
  balance: number;
  available_balance: number;
  currency: string;
  is_primary: boolean;
  status: string;
  daily_limit: number;
  monthly_limit: number;
  created_at: string;
}

interface AccountState {
  accounts: Account[];
  selectedAccount: Account | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: AccountState = {
  accounts: [],
  selectedAccount: null,
  isLoading: false,
  error: null,
};

const accountSlice = createSlice({
  name: 'accounts',
  initialState,
  reducers: {
    fetchAccountsStart: (state) => {
      state.isLoading = true;
      state.error = null;
    },
    fetchAccountsSuccess: (state, action: PayloadAction<Account[]>) => {
      state.isLoading = false;
      state.accounts = action.payload;
      state.error = null;
    },
    fetchAccountsFailure: (state, action: PayloadAction<string>) => {
      state.isLoading = false;
      state.error = action.payload;
    },
    selectAccount: (state, action: PayloadAction<Account>) => {
      state.selectedAccount = action.payload;
    },
    updateAccountBalance: (state, action: PayloadAction<{ accountId: number; balance: number; availableBalance: number }>) => {
      const account = state.accounts.find(acc => acc.id === action.payload.accountId);
      if (account) {
        account.balance = action.payload.balance;
        account.available_balance = action.payload.availableBalance;
      }
      if (state.selectedAccount && state.selectedAccount.id === action.payload.accountId) {
        state.selectedAccount.balance = action.payload.balance;
        state.selectedAccount.available_balance = action.payload.availableBalance;
      }
    },
    addAccount: (state, action: PayloadAction<Account>) => {
      state.accounts.push(action.payload);
    },
    updateAccount: (state, action: PayloadAction<Account>) => {
      const index = state.accounts.findIndex(acc => acc.id === action.payload.id);
      if (index !== -1) {
        state.accounts[index] = action.payload;
      }
      if (state.selectedAccount && state.selectedAccount.id === action.payload.id) {
        state.selectedAccount = action.payload;
      }
    },
    clearError: (state) => {
      state.error = null;
    },
  },
});

export const {
  fetchAccountsStart,
  fetchAccountsSuccess,
  fetchAccountsFailure,
  selectAccount,
  updateAccountBalance,
  addAccount,
  updateAccount,
  clearError,
} = accountSlice.actions;

export default accountSlice.reducer;