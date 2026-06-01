/**
 * HomeScreen - Tela principal
 */
import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';

const HomeScreen = ({ navigation }) => {
  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Projeto Cidadão</Text>
      <Text style={styles.subtitle}>Transparência Pública</Text>
      
      <View style={styles.grid}>
        <TouchableOpacity 
          style={[styles.card, styles.executivo]}
          onPress={() => navigation.navigate('Executivo')}
        >
          <Text style={styles.cardTitle}>Executivo</Text>
          <Text style={styles.cardDesc}>Portal da Transparência, Compras</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.card, styles.legislativo]}
          onPress={() => navigation.navigate('Legislativo')}
        >
          <Text style={styles.cardTitle}>Legislativo</Text>
          <Text style={styles.cardDesc}>Câmara, Senado</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.card, styles.judiciario]}
          onPress={() => navigation.navigate('Judiciario')}
        >
          <Text style={styles.cardTitle}>Judiciário</Text>
          <Text style={styles.cardDesc}>CNJ, Tribunais</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.card, styles.cidadao]}
          onPress={() => navigation.navigate('Fiscalizacao')}
        >
          <Text style={styles.cardTitle}>Fiscalização</Text>
          <Text style={styles.cardDesc}>Acompanhe os gastos</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 16,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginTop: 20,
  },
  subtitle: {
    fontSize: 16,
    color: '#7f8c8d',
    marginBottom: 20,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  card: {
    width: '48%',
    padding: 20,
    borderRadius: 12,
    marginBottom: 16,
  },
  executivo: { backgroundColor: '#27ae60' },
  legislativo: { backgroundColor: '#2980b9' },
  judiciario: { backgroundColor: '#8e44ad' },
  cidadao: { backgroundColor: '#e67e22' },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
  },
  cardDesc: {
    fontSize: 12,
    color: '#ecf0f1',
    marginTop: 4,
  },
});

export default HomeScreen;