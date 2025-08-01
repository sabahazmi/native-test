import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface Transaction {
  id: number;
  transaction_id: string;
  transaction_type: string;
  status: string;
  amount: number;
  currency: string;
  description?: string;
  from_account_id?: number;
  to_account_id?: number;
  from_account_number?: string;
  to_account_number?: string;
  created_at: string;
  processed_at?: string;
  fee_amount: number;
  requires_approval: boolean;
  is_flagged: boolean;
}

interface TransactionState {
  transactions: Transaction[];
  pendingTransactions: Transaction[];
  isLoading: boolean;
  error: string | null;
  pagination: {
    page: number;
    totalPages: number;
    totalItems: number;
    itemsPerPage: number;
  };
}

const initialState: TransactionState = {
  transactions: [],
  pendingTransactions: [],
  isLoading: false,
  error: null,
  pagination: {
    page: 1,
    totalPages: 1,
    totalItems: 0,
    itemsPerPage: 20,
  },
};

const transactionSlice = createSlice({
  name: 'transactions',
  initialState,
  reducers: {
    fetchTransactionsStart: (state) => {
      state.isLoading = true;
      state.error = null;
    },
    fetchTransactionsSuccess: (state, action: PayloadAction<{
      transactions: Transaction[];
      pagination: {
        page: number;
        totalPages: number;
        totalItems: number;
        itemsPerPage: number;
      };
    }>) => {
      state.isLoading = false;
      state.transactions = action.payload.transactions;
      state.pagination = action.payload.pagination;
      state.error = null;
    },
    fetchTransactionsFailure: (state, action: PayloadAction<string>) => {
      state.isLoading = false;
      state.error = action.payload;
    },
    addTransaction: (state, action: PayloadAction<Transaction>) => {
      state.transactions.unshift(action.payload);
      if (action.payload.status === 'pending') {
        state.pendingTransactions.unshift(action.payload);
      }
    },
    updateTransaction: (state, action: PayloadAction<Transaction>) => {
      const index = state.transactions.findIndex(txn => txn.id === action.payload.id);
      if (index !== -1) {
        state.transactions[index] = action.payload;
      }
      
      const pendingIndex = state.pendingTransactions.findIndex(txn => txn.id === action.payload.id);
      if (pendingIndex !== -1) {
        if (action.payload.status === 'pending') {
          state.pendingTransactions[pendingIndex] = action.payload;
        } else {
          state.pendingTransactions.splice(pendingIndex, 1);
        }
      }
    },
    fetchPendingTransactionsSuccess: (state, action: PayloadAction<Transaction[]>) => {
      state.pendingTransactions = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    setPagination: (state, action: PayloadAction<{ page: number }>) => {
      state.pagination.page = action.payload.page;
    },
  },
});

export const {
  fetchTransactionsStart,
  fetchTransactionsSuccess,
  fetchTransactionsFailure,
  addTransaction,
  updateTransaction,
  fetchPendingTransactionsSuccess,
  clearError,
  setPagination,
} = transactionSlice.actions;

export default transactionSlice.reducer;