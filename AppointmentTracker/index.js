import axios from 'axios';
import 'dotenv/config';
import nodemailer from 'nodemailer';
import { DateTime } from 'luxon';

axios.defaults.headers.common['x-troov-web'] = 'com.troov.web';

const api = `https://api.consulat.gouv.fr/api/team/${process.env.URL}/reservations/exclude-days`;

const connect = async () => {
    let transporter = nodemailer.createTransport({
        host: process.env.SMTP_HOST,
        port: process.env.SMTP_PORT,
        secure: false,
        auth: {
          user: process.env.SMTP_EMAIL,
          pass: process.env.SMTP_PASS,
        },
    });

    transporter.verify(function (error) {
        if (error) {
            console.log(error);
            return null;
        }
    });
    return transporter;
}

const sendMail = async (subject, message) => {
    try {
        const data = {
            from: process.env.SMTP_EMAIL,
            to: process.env.TO_EMAIL,
            subject: subject,
            text: message
        };
        let transporter = await connect();
        if (transporter) {
            await transporter.sendMail(data);
        }
        else {
            console.log('SMTP Error');    
        }
    }
    catch (error) {
        console.log('Mail failed to send');
    }
}

const cleanDate = (date) => date.toISO().slice(0, -10);

const checkCanRegister = async () => {
    const startDate = DateTime.now().setZone('America/Guayaquil');
    const endDate = startDate.plus({days: 33});
    const payload = {
        "start": cleanDate(startDate),
        "end": cleanDate(endDate),
        "session": {
            [process.env.SESSION]: 1
        }
    };
    const resp = await axios.post(api, payload);
    const dates = new Set(resp.data);
    let today = startDate;

    while  (today <= endDate) {
        let todayString = today.toISODate();
        if (!dates.has(todayString)) {
            sendMail("Register - Date is available!", `Run! ${todayString} should be available! https://consulat.gouv.fr/ambassade-de-france-a-quito/rendez-vous?name=Visa`);
            console.log('Date found!', todayString);
            return;
        }
        today = today.plus({days: 1});
    }
    console.log('No available date found');
}

const checkIfDateStillAvaialable = async () => {
    const payload = {
        "start": process.env.START,
        "end": process.env.END,
        "session": {
            [process.env.SESSION]: 1
        }
    }
    const resp = await axios.post(api, payload);
    const dates = new Set(resp.data);
    if (dates.has(process.env.TARGET)) {
        console.log(`${'Date is no longer available!'}`);
        sendMail('Check - Date is no longer available', 'Date has been added to exclude dates');
    }
    else {
        console.log(`${'Date is still available'}`)
    }
}

try {
    //await checkIfDateStillAvaialable();
    await checkCanRegister();
}
catch (error) {
    sendMail('Error', error.toString());
    console.error(error);
}