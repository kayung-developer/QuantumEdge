import React from 'react';
import { useForm, Controller } from 'react-hook-form';
import toast from 'react-hot-toast';
import Button from '../components/common/Button';
import { FiDownload } from 'react-icons/fi';
// An API service for reports would be created
// import reportService from '../api/reportService';

const ReportsPage = () => {
    const { control, handleSubmit } = useForm({
        defaultValues: {
            start_date: '2023-01-01',
            end_date: '2023-12-31',
        }
    });

    const onSubmit = async (data) => {
        toast.loading("Generating your report...");
        try {
            // The service would call the API and handle the file download
            // await reportService.downloadTradeHistory(data.start_date, data.end_date);
            // For now, we simulate the link click
            const url = `${import.meta.env.VITE_API_BASE_URL}/reports/export/trade-history?start_date=${data.start_date}T00:00:00Z&end_date=${data.end_date}T23:59:59Z`;
            // Add auth token for download (this is a simplified approach)
            const token = localStorage.getItem('accessToken');
            const finalUrl = `${url}&token=${token}`; // A backend dep would parse this
            window.open(finalUrl, '_blank');

            toast.success("Your download will begin shortly.");
        } catch (error) {
            toast.error("Failed to generate report.");
        }
    };

    return (
        <div className="p-6 animate-fadeIn max-w-lg mx-auto">
            <h1 className="text-3xl font-bold mb-6">Export Reports</h1>
            <div className="bg-dark-surface p-6 rounded-lg">
                <h2 className="text-xl font-semibold">Trade History (CSV)</h2>
                <p className="text-text-secondary mt-2 mb-4">
                    Download a complete log of your filled trades for a specific period. This is useful for tax purposes and personal record-keeping.
                </p>
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                     <div>
                        <label>Start Date</label>
                        <Controller name="start_date" control={control} render={({ field }) => ( <input {...field} type="date" className="w-full bg-dark-background p-2 rounded-md mt-1"/> )}/>
                     </div>
                     <div>
                        <label>End Date</label>
                        <Controller name="end_date" control={control} render={({ field }) => ( <input {...field} type="date" className="w-full bg-dark-background p-2 rounded-md mt-1"/> )}/>
                     </div>
                     <Button type="submit" className="w-full">
                        <FiDownload className="mr-2"/>
                        Download Report
                     </Button>
                </form>
            </div>
        </div>
    );
};

export default ReportsPage;
