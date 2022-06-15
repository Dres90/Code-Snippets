import axios from 'axios';
import 'dotenv/config';
import nodemailer from 'nodemailer';

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

    transporter.verify(function (error, success) {
    if (error) {
        console.log(error);
        return null;
    } else {
        console.log("Server is ready to take our messages");
    }
    });
    return transporter;
}

const getMessage = (target) => {
    return {
        from: process.env.SMTP_EMAIL,
        to: process.env.TO_EMAIL,
        subject: "Date is no longer available",
        text: `The target ${target} date is no longer available! Time: ${new Date().toISOString()}`
    };
}

try {
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
        let transporter = await connect();
        if (transporter) {
            transporter.sendMail(getMessage(process.env.TARGET));
        }
    }
    else {
        console.log(`${'Date is still available'}`)
    }
}
catch (error) {
    console.error(error);
}