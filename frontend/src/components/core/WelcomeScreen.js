import React, { useState, useEffect } from 'react';
import { useAuth } from 'contexts/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';
import { Logo } from './Icons';

const WelcomeScreen = () => {
    const { user } = useAuth();
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        const isFirstLogin = !localStorage.getItem('has_logged_in_before');
        if (isFirstLogin) {
            setIsVisible(true);
            localStorage.setItem('has_logged_in_before', 'true');
        }
    }, []);

    const variants = {
        hidden: { opacity: 0, y: 50 },
        visible: (i) => ({
            opacity: 1,
            y: 0,
            transition: {
                delay: i * 0.3,
                duration: 0.8,
                ease: "easeOut"
            },
        }),
    };

    if (!isVisible) {
        return null;
    }

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 bg-dark-bg/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            >
                <div className="text-center">
                    <motion.div variants={variants} initial="hidden" animate="visible" custom={0}>
                        <Logo className="h-24 w-auto text-primary mx-auto" />
                    </motion.div>
                    <motion.h1 variants={variants} initial="hidden" animate="visible" custom={1} className="text-5xl font-extrabold text-white mt-8">
                        Welcome, {user?.full_name?.split(' ')[0]}
                    </motion.h1>
                    <motion.p variants={variants} initial="hidden" animate="visible" custom={2} className="text-xl text-gray-300 mt-4 max-w-2xl mx-auto">
                        You're all set to revolutionize your trading. Let's get started.
                    </motion.p>
                    <motion.button
                        variants={variants} initial="hidden" animate="visible" custom={3}
                        onClick={() => setIsVisible(false)}
                        className="mt-10 px-8 py-4 bg-primary text-white font-bold text-lg rounded-xl shadow-lg hover:bg-primary-700 transition-transform hover:scale-105"
                    >
                        Enter the Dashboard
                    </motion.button>
                </div>
            </motion.div>
        </AnimatePresence>
    );
};

export default WelcomeScreen;