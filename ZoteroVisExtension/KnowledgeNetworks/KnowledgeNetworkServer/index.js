const express = require('express')
const app = express()
const port = 3000

app.get('/zotero', async (req, res) => {
  const response = await fetch("http://localhost:23119/api/users/0/items?limit=10&sort=dateAdded");
  console.log(await response.json())
})
app.listen(port, () => {
  console.log(`Example app listening on port ${port}`)
})
