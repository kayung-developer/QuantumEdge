import React, { useState, useEffect, Fragment } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import api from 'services/api';
import ReactMarkdown from 'react-markdown'; // You might need to install this: npm install react-markdown

const ChangelogModal = ({ isOpen, onClose }) => {
    const [changelog, setChangelog] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (isOpen) {
            api.get('/system/changelog')
                .then(res => setChangelog(res.data))
                .catch(err => console.error("Failed to fetch changelog", err))
                .finally(() => setLoading(false));
        }
    }, [isOpen]);

    return (
        <Transition appear show={isOpen} as={Fragment}>
            <Dialog as="div" className="relative z-30" onClose={onClose}>
                {/* ... (Overlay and centering logic) ... */}
                <div className="fixed inset-0 overflow-y-auto">
                    <div className="flex min-h-full items-center justify-center p-4">
                        <Dialog.Panel className="w-full max-w-2xl transform overflow-hidden rounded-2xl bg-white dark:bg-dark-card p-6 text-left align-middle shadow-xl transition-all">
                            <Dialog.Title as="h3" className="text-xl font-bold leading-6 text-gray-900 dark:text-white">
                                What's New
                            </Dialog.Title>
                            <div className="mt-4 max-h-96 overflow-y-auto pr-2">
                                {loading ? <p>Loading...</p> : (
                                    changelog.map(entry => (
                                        <div key={entry.version} className="mb-6 pb-6 border-b dark:border-dark-border last:border-b-0">
                                            <div className="flex items-baseline space-x-3">
                                                <span className="px-2 py-1 bg-primary text-white text-sm font-semibold rounded">{entry.version}</span>
                                                <h4 className="text-lg font-semibold">{entry.title}</h4>
                                            </div>
                                            <p className="text-xs text-gray-500 mt-1">{new Date(entry.release_date).toLocaleDateString()}</p>
                                            <div className="prose dark:prose-invert mt-2 text-sm">
                                                <ReactMarkdown>{entry.summary}</ReactMarkdown>
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                            <div className="mt-4">
                                <button type="button" onClick={onClose} className="w-full px-4 py-2 text-sm font-medium rounded-md bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600">
                                    Close
                                </button>
                            </div>
                        </Dialog.Panel>
                    </div>
                </div>
            </Dialog>
        </Transition>
    );
};

export default ChangelogModal;