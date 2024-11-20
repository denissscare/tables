import React, { useEffect, useState } from "react";
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from "@mui/material";
import axios from "axios";

const App = () => {
  const [metrics, setMetrics] = useState({});
  const [trades, setTrades] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get("https://api.meridian.trade/api/get_test_data?id=72N6LvBOj");
        const data = response.data;
        console.log(data.closeTrades)
        setMetrics(data.metrics);
        setTrades(data.closeTrades);
      } catch (error) {
        console.error("Ошибка при получении данных:", error);
      }
    };
    fetchData();
  }, []);

  return (
    <div style={{ padding: "20px" }}>
      <h1>Анализ сделок</h1>

      {/* Таблица метрик */}
      <h2>Метрики</h2>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Метрика</TableCell>
              <TableCell>Значение</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {Object.entries(metrics).map(([key, value]) => (
              <TableRow key={key}>
                <TableCell>{key}</TableCell>
                <TableCell>{value}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Таблица сделок */}
      <h2>Список закрытых сделок</h2>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID сделки</TableCell>
              <TableCell>Дата открытия</TableCell>
              <TableCell>Дата закрытия</TableCell>
              <TableCell>Цена открытия</TableCell>
              <TableCell>Цена закрытия</TableCell>
              <TableCell>Прибыль</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {trades.map((trade, index) => (
              <TableRow key={index}>
                <TableCell>{trade["ID"]}</TableCell>
                <TableCell>{trade["Дата открытия"]}</TableCell>
                <TableCell>{trade["Дата закрытия"]}</TableCell>
                <TableCell>{trade["Цена открытия"]}</TableCell>
                <TableCell>{trade["Цена закрытия"]}</TableCell>
                <TableCell>{trade["Прибыль"]}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </div>
  );
};

export default App;