import React, { Fragment } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import Button from './Button';
import { FiAlertTriangle } from 'react-icons/fi';
import { clsx } from 'clsx';

/**
 * A generic, accessible modal for confirming critical actions (e.g., deletion).
 * It prevents accidental destructive operations.
 *
 * @param {boolean} isOpen - Controls the visibility of the modal.
 * @param {function} onClose - Function to call when the modal is closed (e.g., clicking backdrop or cancel).
 * @param {function} onConfirm - Function to call when the confirm button is clicked.
 * @param {string} title - The title of the modal.
 * @param {string} description - The descriptive text explaining the action.
 * @param {string} [confirmText='Confirm'] - The text for the confirmation button.
 * @param {string} [cancelText='Cancel'] - The text for the cancel button.
 * @param {string} [intent='danger'] - 'danger' for destructive actions (red), 'primary' for others (blue).
 */
const ConfirmationModal = ({
    isOpen,
    onClose,
    onConfirm,
    title,
    description,
    confirmText = 'Confirm',
    cancelText = 'Cancel',
    intent = 'danger'
}) => {
    return (
        <Transition appear show={isOpen} as={Fragment}>
            <Dialog as="div" className="relative z-50" onClose={onClose}>
                <Transition.Child as={Fragment} enter="ease-out duration-300" enterFrom="opacity-0" enterTo="opacity-100" leave="ease-in duration-200" leaveFrom="opacity-100" leaveTo="opacity-0">
                    <div className="fixed inset-0 bg-black bg-opacity-60" />
                </Transition.Child>
                <div className="fixed inset-0 overflow-y-auto">
                    <div className="flex min-h-full items-center justify-center p-4 text-center">
                        <Transition.Child as={Fragment} enter="ease-out duration-300" enterFrom="opacity-0 scale-95" enterTo="opacity-100 scale-100" leave="ease-in duration-200" leaveFrom="opacity-100 scale-100" leaveTo="opacity-0 scale-95">
                            <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-dark-surface p-6 text-left align-middle shadow-xl transition-all border border-dark-secondary">
                                <div className="sm:flex sm:items-start">
                                    <div className={clsx('mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full sm:mx-0 sm:h-10 sm:w-10', intent === 'danger' ? 'bg-danger/10' : 'bg-brand-primary/10')}>
                                        <FiAlertTriangle className={clsx('h-6 w-6', intent === 'danger' ? 'text-danger' : 'text-brand-primary')} aria-hidden="true" />
                                    </div>
                                    <div className="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                                        <Dialog.Title as="h3" className="text-lg font-bold leading-6 text-text-primary">{title}</Dialog.Title>
                                        <div className="mt-2"><p className="text-sm text-text-secondary">{description}</p></div>
                                    </div>
                                </div>
                                <div className="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
                                    <Button onClick={onConfirm} className={clsx('w-full sm:ml-3 sm:w-auto', intent === 'danger' ? 'bg-danger hover:bg-red-700 focus:ring-danger' : 'bg-brand-primary hover:bg-blue-500 focus:ring-brand-primary')}>
                                        {confirmText}
                                    </Button>
                                    <Button onClick={onClose} variant="secondary" className="mt-3 w-full sm:mt-0 sm:w-auto">
                                        {cancelText}
                                    </Button>
                                </div>
                            </Dialog.Panel>
                        </Transition.Child>
                    </div>
                </div>
            </Dialog>
        </Transition>
    );
};

export default ConfirmationModal;