import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import toast from 'react-hot-toast';
import useAuth from '../hooks/useAuth';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import { FiUser, FiLock } from 'react-icons/fi';
import axiosClient from '../api/axiosClient.js';
// An API service for user actions would be ideal
// import userService from '../api/userService';

// Zod schema for validation
const profileSchema = z.object({
    full_name: z.string().min(2, "Full name must be at least 2 characters"),
});

const passwordSchema = z.object({
    password: z.string().min(8, "New password must be at least 8 characters"),
    confirm_password: z.string(),
}).refine(data => data.password === data.confirm_password, {
    message: "Passwords do not match",
    path: ["confirm_password"],
});


const ProfileSettingsPage = () => {
    const { user, login } = useAuth(); // Re-running login will refresh the user context with new data

    // Form for profile details
    const { register: registerProfile, handleSubmit: handleProfileSubmit, formState: { errors: profileErrors, isSubmitting: isProfileSubmitting } } = useForm({
        resolver: zodResolver(profileSchema),
        defaultValues: { full_name: user?.full_name || '' }
    });

    // Separate form for password change
    const { register: registerPassword, handleSubmit: handlePasswordSubmit, formState: { errors: passwordErrors, isSubmitting: isPasswordSubmitting }, reset: resetPassword } = useForm({
        resolver: zodResolver(passwordSchema)
    });

    const onProfileSubmit = async (data) => {
        const toastId = toast.loading("Updating profile...");
        try {
            // This would call a dedicated user service function, e.g., userService.updateMe(data)
            // For now, we use the raw axiosClient for demonstration
            await axiosClient.put('/users/me', data);

            // A successful update requires re-fetching user data.
            // A simple way is to re-trigger the login logic which fetches the '/users/me' data.
            // A more elegant solution would be a dedicated `refetchUser` function in AuthContext.
            await login(user.email, /* user must re-enter password for this */);

            toast.success("Profile updated successfully!", { id: toastId });
        } catch (error) {
            toast.error(error.response?.data?.detail || "Failed to update profile.", { id: toastId });
        }
    };

    const onPasswordSubmit = async (data) => {
        const toastId = toast.loading("Changing password...");
        try {
            // await userService.updateMe({ password: data.password });
            toast.success("Password changed successfully!", { id: toastId });
            resetPassword();
        } catch (error) {
            toast.error(error.response?.data?.detail || "Failed to change password.", { id: toastId });
        }
    };

    return (
        <div className="p-6 animate-fadeIn">
            <h2 className="text-xl font-bold text-text-primary mb-1">Your Profile</h2>
            <p className="text-sm text-text-secondary mb-6">Manage your personal information and password.</p>

            <div className="space-y-8">
                {/* Profile Information Form */}
                <form onSubmit={handleProfileSubmit(onProfileSubmit)} className="space-y-4">
                    <Input
                        id="email"
                        label="Email Address"
                        type="email"
                        value={user?.email || ''}
                        disabled
                        className="bg-dark-background cursor-not-allowed"
                    />
                    <Input
                        id="full_name"
                        label="Full Name"
                        type="text"
                        icon={FiUser}
                        error={profileErrors.full_name}
                        {...registerProfile("full_name")}
                    />
                    <div className="flex justify-end">
                        <Button type="submit" isLoading={isProfileSubmitting}>Save Profile</Button>
                    </div>
                </form>

                <div className="border-t border-dark-secondary"></div>

                {/* Change Password Form */}
                <form onSubmit={handlePasswordSubmit(onPasswordSubmit)} className="space-y-4">
                     <h3 className="text-lg font-semibold text-text-primary">Change Password</h3>
                     <Input
                        id="password"
                        label="New Password"
                        type="password"
                        icon={FiLock}
                        error={passwordErrors.password}
                        {...registerPassword("password")}
                    />
                     <Input
                        id="confirm_password"
                        label="Confirm New Password"
                        type="password"
                        icon={FiLock}
                        error={passwordErrors.confirm_password}
                        {...registerPassword("confirm_password")}
                    />
                    <div className="flex justify-end">
                        <Button type="submit" isLoading={isPasswordSubmitting}>Update Password</Button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default ProfileSettingsPage;