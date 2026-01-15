import  api from 'zotero-api-client';
import axios from 'axios'
const myapi = api(16478194).library('user', 0);
async function getData(){
 // const response = await api().library('user', 16478194).collections('9KH9TNSJ').items().get();
  const response = await fetch("http://localhost:23119/api/users/0/items?limit=10&sort=dateAdded", {
    }
  )
  console.log(response)

}
export default getData;
