/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'https://3.134.26.61:81', // the running FLASK api server url
  auth0: {
    url: 'https://dcadventuresonline.us.auth0.com', // the auth0 domain prefix
    audience: 'coffe', // the audience set for the auth0 app
    clientId: 'p3kGaVETQ4TA3BibSj7UKPeSbS5bZ5I5', // the client id generated for the auth0 app
    callbackURL: 'https://3.134.26.61:80', // the base url of the running ionic application. 
  }
};
