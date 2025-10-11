import React from 'react';
import Joyride, { STATUS } from 'react-joyride';
import { useTranslation } from 'react-i18next';

/**
 * A component that provides a guided tour for new users, powered by react-joyride.
 * @param {boolean} run - State to control whether the tour is active.
 * @param {function} setRunTour - Function to update the run state.
 */
const WelcomeTour = ({ run, setRunTour }) => {
  const { t } = useTranslation();

  const tourSteps = [
    {
      target: '#tour-step-1-sidebar',
      content: t('tour.step1'),
      placement: 'right',
      disableBeacon: true,
    },
    {
      target: '#tour-step-2-header',
      content: t('tour.step2'),
      placement: 'bottom',
    },
    {
      target: '#tour-step-3-main-content',
      content: t('tour.step3'),
      placement: 'top',
    },
    {
      target: '#tour-step-4-trading-link',
      content: t('tour.step4'),
      placement: 'right',
    },
  ];

  const handleJoyrideCallback = (data) => {
    const { status } = data;
    if ([STATUS.FINISHED, STATUS.SKIPPED].includes(status)) {
      setRunTour(false);
      // Set a flag in localStorage so the tour doesn't automatically
      // show again for this user.
      localStorage.setItem('auraquant-tour-completed', 'true');
    }
  };

  return (
    <Joyride
      run={run}
      steps={tourSteps}
      continuous
      showProgress
      showSkipButton
      callback={handleJoyrideCallback}
      styles={{
        options: {
          arrowColor: '#161B22',
          backgroundColor: '#161B22',
          primaryColor: '#3B82F6',
          textColor: '#E6EDF3',
          zIndex: 10000,
          borderRadius: '8px',
        },
        buttonClose: { color: '#8B949E' },
        buttonNext: { backgroundColor: '#3B82F6', borderRadius: '6px' },
        buttonBack: { color: '#8B949E' },
        tooltip: { padding: '20px' },
      }}
    />
  );
};

export default WelcomeTour;