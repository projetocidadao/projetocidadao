/**
 * ExecutivoScreen - Dados do Executivo
 */
import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, FlatList } from 'react-native';
import { getBolsaFamilia, getConvenios, getLicitacoes } from '../services/api';

const ExecutivoScreen = () => {
  const [cpf, setCpf] = useState('');
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('bolsa');

  const searchBolsaFamilia = async () => {
    setLoading(true);
    try {
      const response = await getBolsaFamilia(cpf);
      setData(response.data);
    } catch (error) {
      console.error(error);
    }
    setLoading(false);
  };

  const searchConvenios = async () => {
    setLoading(true);
    try {
      const response = await getConvenios(cpf);
      setData(response.data);
    } catch (error) {
      console.error(error);
    }
    setLoading(false);
  };

  const searchLicitacoes = async () => {
    setLoading(true);
    try {
      const response = await getLicitacoes(null, null, 2024);
      setData(response.data);
    } catch (error) {
      console.error(error);
    }
    setLoading(false);
  };

  const renderItem = ({ item }) => (
    <View style={styles.item}>
      <Text style={styles.itemText}>{JSON.stringify(item).substring(0, 100)}</Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Executivo</Text>
      
      <View style={styles.tabs}>
        <TouchableOpacity 
          style={[styles.tab, activeTab === 'bolsa' && styles.activeTab]}
          onPress={() => setActiveTab('bolsa')}
        >
          <Text style={styles.tabText}>Bolsa Família</Text>
        </TouchableOpacity>
        <TouchableOpacity 
          style={[styles.tab, activeTab === 'convenios' && styles.activeTab]}
          onPress={() => setActiveTab('convenios')}
        >
          <Text style={styles.tabText}>Convênios</Text>
        </TouchableOpacity>
        <TouchableOpacity 
          style={[styles.tab, activeTab === 'licitacoes' && styles.activeTab]}
          onPress={() => setActiveTab('licitacoes')}
        >
          <Text style={styles.tabText}>Licitações</Text>
        </TouchableOpacity>
      </View>

      <TextInput
        style={styles.input}
        placeholder="Digite CPF ou CNPJ"
        value={cpf}
        onChangeText={setCpf}
        keyboardType="numeric"
      />

      <TouchableOpacity style={styles.button} onPress={
        activeTab === 'bolsa' ? searchBolsaFamilia :
        activeTab === 'convenios' ? searchConvenios : searchLicitacoes
      }>
        <Text style={styles.buttonText}>Buscar</Text>
      </TouchableOpacity>

      <FlatList
        data={data}
        renderItem={renderItem}
        keyExtractor={(item, index) => index.toString()}
        style={styles.list}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#27ae60',
    marginBottom: 16,
  },
  tabs: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  tab: {
    flex: 1,
    padding: 10,
    backgroundColor: '#ddd',
    alignItems: 'center',
  },
  activeTab: {
    backgroundColor: '#27ae60',
  },
  tabText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  input: {
    backgroundColor: '#fff',
    padding: 12,
    borderRadius: 8,
    marginBottom: 12,
  },
  button: {
    backgroundColor: '#27ae60',
    padding: 14,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 16,
  },
  buttonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  list: {
    flex: 1,
  },
  item: {
    backgroundColor: '#fff',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  itemText: {
    fontSize: 14,
  },
});

export default ExecutivoScreen;