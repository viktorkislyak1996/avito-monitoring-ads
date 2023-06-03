db = db.getSiblingDB("avito_ads");
db.createUser({
  user: "user1",
  pwd: "11223344",
  roles: [
    {
      role: "readWrite",
      db: "avito_ads",
    },
  ],
});
