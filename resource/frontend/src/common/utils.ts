import { Notify } from 'quasar'

export function inIframe() {
  try {
    return window.self !== window.top
  } catch (e) {
    return true
  }
}

export function createNotification(type: 'positive' | 'negative', msg: string) {
  if (type === 'positive') {
    Notify.create({
      type: 'positive',
      message: msg,
      position: 'top',
      color: 'positive-alert',
      textColor: 'positive-alert',
      icon: 'check',
      iconSize:'sm',
      classes: 'bs-font-medium-1-semi-bold bs-alert-notification',
      actions: [
        {
          icon: 'close',
          color: 'positive-alert',
          padding:'0px',
          size:'sm',
          round: true
        }
      ],
    })
  } else {
    Notify.create({
      type: 'negative',
      message: msg,
      position: 'top',
      color: 'negative-alert',
      textColor: 'negative-alert',
      icon: 'warning',
      iconSize:'sm',
      classes: 'bs-font-medium-1-semi-bold bs-alert-notification',
      actions: [
        {
          icon: 'close',
          color: 'negative-alert',
          round: true,
          padding:'0px',
          size:'sm',
        }
      ]
    })
  }
}
