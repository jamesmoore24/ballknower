export const isDevelopment = process.env.NODE_ENV === "development";
export const isProduction = process.env.NODE_ENV === "production";

export const getDbConfig = () => {
  // Development: Use local SQLite file
  if (isDevelopment) {
    return {
      path: "./cron/ballknower.db",
      readOnly: false,
    };
  }

  // Production: Use the configured path
  if (isProduction) {
    return {
      path: "/home/ec2-user/data/ballknower.db",
      readOnly: false,
    };
  }

  // Build time: Use in-memory database
  return {
    path: ":memory:",
    readOnly: true,
  };
};
