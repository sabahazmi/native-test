import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface Notification {
  id: number;
  title: string;
  message: string;
  notification_type: string;
  priority: string;
  is_read: boolean;
  created_at: string;
  action_url?: string;
}

interface NotificationState {
  notifications: Notification[];
  unreadCount: number;
  isLoading: boolean;
  error: string | null;
}

const initialState: NotificationState = {
  notifications: [],
  unreadCount: 0,
  isLoading: false,
  error: null,
};

const notificationSlice = createSlice({
  name: 'notifications',
  initialState,
  reducers: {
    fetchNotificationsStart: (state) => {
      state.isLoading = true;
      state.error = null;
    },
    fetchNotificationsSuccess: (state, action: PayloadAction<Notification[]>) => {
      state.isLoading = false;
      state.notifications = action.payload;
      state.unreadCount = action.payload.filter(n => !n.is_read).length;
      state.error = null;
    },
    fetchNotificationsFailure: (state, action: PayloadAction<string>) => {
      state.isLoading = false;
      state.error = action.payload;
    },
    addNotification: (state, action: PayloadAction<Notification>) => {
      state.notifications.unshift(action.payload);
      if (!action.payload.is_read) {
        state.unreadCount += 1;
      }
    },
    markAsRead: (state, action: PayloadAction<number[]>) => {
      action.payload.forEach(id => {
        const notification = state.notifications.find(n => n.id === id);
        if (notification && !notification.is_read) {
          notification.is_read = true;
          state.unreadCount -= 1;
        }
      });
    },
    markAllAsRead: (state) => {
      state.notifications.forEach(notification => {
        notification.is_read = true;
      });
      state.unreadCount = 0;
    },
    removeNotification: (state, action: PayloadAction<number>) => {
      const index = state.notifications.findIndex(n => n.id === action.payload);
      if (index !== -1) {
        const notification = state.notifications[index];
        if (!notification.is_read) {
          state.unreadCount -= 1;
        }
        state.notifications.splice(index, 1);
      }
    },
    clearError: (state) => {
      state.error = null;
    },
  },
});

export const {
  fetchNotificationsStart,
  fetchNotificationsSuccess,
  fetchNotificationsFailure,
  addNotification,
  markAsRead,
  markAllAsRead,
  removeNotification,
  clearError,
} = notificationSlice.actions;

export default notificationSlice.reducer;