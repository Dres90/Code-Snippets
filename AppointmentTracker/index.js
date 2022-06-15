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
}

const cleanDate = (date) => date.toISO().slice(0, -10);

const checkCanRegister = async () => {
    const targetDate = DateTime.fromISO(process.env.TARGET, {zone: 'America/Guayaquil'});
    const startDate = DateTime.now().setZone('America/Guayaquil');
    const endDate = startDate.plus({days: 33});
    if (targetDate < startDate || targetDate > endDate) {
        console.log('Date outside margin');
        return;
    };
    const payload = {
        "start": cleanDate(startDate),
        "end": cleanDate(endDate),
        "session": {
            [process.env.SESSION]: 1
        }
    };
    const resp = await axios.post(api, payload);
    const dates = new Set(resp.data);
    if (!dates.has(process.env.TARGET)) {
        sendMail("Register - Date is available!", `Run! ${process.env.TARGET} should be available! https://consulat.gouv.fr/ambassade-de-france-a-quito/rendez-vous?name=Visa`);
    }
    else {
        sendMail("Register - Date is not available!", "You have been scammed, date was not available");
    }
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
    await checkIfDateStillAvaialable();
    await checkCanRegister();
}
catch (error) {
    console.error(error);
}