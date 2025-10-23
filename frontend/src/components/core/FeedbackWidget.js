import React, { useState, Fragment } from 'react';
import { Popover, Transition } from '@headlessui/react';
import { useForm } from 'react-hook-form';
import api from 'services/api';
import toast from 'react-hot-toast';
import { ChatBubbleLeftRightIcon } from '@heroicons/react/24/solid';

// We create a separate component for the panel content.
// This allows us to pass the `close` function from the Popover render prop
// down to where the form submission happens.
const FeedbackPanel = ({ close }) => {
    const { register, handleSubmit, reset } = useForm();

    const onSubmit = async (data) => {
        const promise = api.post('/system/feedback', {
            ...data,
            page: window.location.pathname
        });

        toast.promise(promise, {
            loading: 'Submitting feedback...',
            success: () => {
                reset(); // Clear the form fields
                close(); // Programmatically close the popover on success
                return 'Thank you for your feedback!';
            },
            error: 'Failed to submit feedback.',
        });
    };

    return (
        <div className="overflow-hidden rounded-lg shadow-lg ring-1 ring-black ring-opacity-5">
            <div className="relative bg-white dark:bg-dark-card p-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">Submit Feedback</h3>
                <form onSubmit={handleSubmit(onSubmit)} className="mt-4 space-y-4">
                    <div>
                        <label htmlFor="feedback_type" className="sr-only">Feedback Type</label>
                        <select id="feedback_type" {...register("feedback_type")} className="w-full rounded-md border-gray-300 dark:bg-gray-800 dark:border-dark-border focus:ring-primary focus:border-primary">
                            <option value="suggestion">Suggestion</option>
                            <option value="bug">Bug Report</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                    <div>
                        <label htmlFor="feedback_message" className="sr-only">Message</label>
                        <textarea
                            id="feedback_message"
                            {...register("message", { required: true, minLength: 10 })}
                            rows="5"
                            placeholder="Tell us what you think..."
                            className="w-full rounded-md border-gray-300 dark:bg-gray-800 dark:border-dark-border focus:ring-primary focus:border-primary"
                        ></textarea>
                    </div>
                    <button type="submit" className="w-full py-2 bg-success text-white font-semibold rounded-md hover:bg-green-600 transition-colors">
                        Send Feedback
                    </button>
                </form>
            </div>
        </div>
    );
};


const FeedbackWidget = () => {
    // --- THIS IS THE CORRECT STRUCTURE ---
    // All hooks are at the top level of the main component.
    // The logic is clean and follows React's rules.

    return (
        <div className="fixed bottom-5 right-5 z-20">
            <Popover>
                {/* The render prop provides the 'close' function */}
                {({ close }) => (
                    <>
                        <Popover.Button className="flex items-center gap-2 px-4 py-2 bg-primary text-white font-semibold rounded-full shadow-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-transform transform hover:scale-105">
                            <ChatBubbleLeftRightIcon className="h-5 w-5"/>
                            Feedback
                        </Popover.Button>
                        <Transition
                            as={Fragment}
                            enter="transition ease-out duration-200"
                            enterFrom="opacity-0 translate-y-1"
                            enterTo="opacity-100 translate-y-0"
                            leave="transition ease-in duration-150"
                            leaveFrom="opacity-100 translate-y-0"
                            leaveTo="opacity-0 translate-y-1"
                        >
                            <Popover.Panel className="absolute bottom-full right-0 w-80 mb-2 transform">
                                {/* We render the new component and pass the 'close' function to it */}
                                <FeedbackPanel close={close} />
                            </Popover.Panel>
                        </Transition>
                    </>
                )}
            </Popover>
        </div>
    );
};

export default FeedbackWidget;