import axios from 'axios';
import 'dotenv/config';
import nodemailer from 'nodemailer';


const api = `https://www.apple.com/es/shop/fulfillment-messages`;
const params = {
    // 'store': 'R406',
    'store': 'R368',
    'parts.0': 'MU773QL/A',
    'parts.1': 'MU783QL/A',
    'parts.2': 'MU7A3QL/A',
    'parts.3': 'MU793QL/A',
    // 'parts.4': 'MTV63QL/A'
}

const connect = async () => {
    let transporter = nodemailer.createTransport({
        host: process.env.SMTP_HOST,
        port: process.env.SMTP_PORT,
        secure: false,
        auth: {
          user: process.env.SMTP_USER,
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
        console.log('Mail failed to send', error);
    }
}


const checkIphoneAvailable = async () => {

    const resp = await axios.get(api, { params });
    
    const { partsAvailability } = resp.data.body.content.pickupMessage.stores[0];

    let availability = [];

    for (let model in partsAvailability) {
        const part = partsAvailability[model];
        if (part.pickupDisplay != 'unavailable' ) {
            const { storePickupQuote, storePickupProductTitle } = part.messageTypes.regular;
            availability.push([storePickupProductTitle, storePickupQuote]);
        }
    }

    if (availability.length > 0) {
        let message = '';
        for (const part of availability) {
            message += `${part[0]} - ${part[1]}\n`;
        }
        console.log('Availability found!');
        sendMail("Iphone is Available!", message);
    }
    else {
        console.log('No availability found');
    }
}

try {
    await checkIphoneAvailable();
}
catch (error) {
    //sendMail('Error', error.toString());
    console.error(error);
}