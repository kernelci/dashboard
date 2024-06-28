import React from 'react'
import ReactDOM from 'react-dom/client'

import {IntlProvider} from "react-intl";

import {flatten} from 'flat';

import {messages} from './locales/messages/index'
import {LOCALES} from './locales/constants'



import './index.css'
import App from './App'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <IntlProvider messages={flatten(messages[LOCALES.EN_US])} locale='en' >
      <App />
    </IntlProvider>
    
  </React.StrictMode>,
)
