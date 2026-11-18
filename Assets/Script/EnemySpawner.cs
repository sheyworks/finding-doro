using System;
using System.Collections.Generic;
using UnityEngine;

public class EnemySpawner : MonoBehaviour
{
    [Serializable]
    public class SpawnArea
    {
        [Tooltip("Posisi, rotasi, dan scale Transform ini menentukan volume area spawn.")]
        public Transform center;
    }

    [Header("Spawn Areas")]
    [SerializeField] private List<SpawnArea> spawnAreas = new List<SpawnArea>();

    [Header("Enemy Types")]
    [SerializeField] private List<GameObject> enemyPrefabs = new List<GameObject>();

    [Header("Spawn Settings")]
    [SerializeField] private bool spawnOnStart = true;
    [SerializeField] private float spawnInterval = 5f;
    [SerializeField] private int maxAliveEnemies = 8;
    [SerializeField] private Transform spawnedEnemyParent;

    private readonly List<GameObject> spawnedEnemies = new List<GameObject>();
    private float nextSpawnTime;

    private void Start()
    {
        if (spawnOnStart) SpawnEnemy();
        nextSpawnTime = Time.time + Mathf.Max(0.1f, spawnInterval);
    }

    private void Update()
    {
        spawnedEnemies.RemoveAll(enemy => enemy == null);

        if (Time.time < nextSpawnTime) return;
        nextSpawnTime = Time.time + Mathf.Max(0.1f, spawnInterval);

        if (spawnedEnemies.Count < maxAliveEnemies)
        {
            SpawnEnemy();
        }
    }

    public GameObject SpawnEnemy()
    {
        spawnedEnemies.RemoveAll(enemy => enemy == null);
        if (spawnedEnemies.Count >= maxAliveEnemies) return null;

        List<GameObject> validPrefabs = enemyPrefabs.FindAll(prefab => prefab != null);
        List<SpawnArea> validAreas = spawnAreas.FindAll(area => area != null && area.center != null);
        if (validPrefabs.Count == 0 || validAreas.Count == 0) return null;

        GameObject prefab = validPrefabs[UnityEngine.Random.Range(0, validPrefabs.Count)];
        SpawnArea area = validAreas[UnityEngine.Random.Range(0, validAreas.Count)];
        Vector3 areaScale = area.center.lossyScale;
        float halfWidth = Mathf.Abs(areaScale.x) * 0.5f;
        float halfHeight = Mathf.Abs(areaScale.y) * 0.5f;
        float halfDepth = Mathf.Abs(areaScale.z) * 0.5f;

        Vector3 randomOffset = new Vector3(
            UnityEngine.Random.Range(-halfWidth, halfWidth),
            UnityEngine.Random.Range(-halfHeight, halfHeight),
            UnityEngine.Random.Range(-halfDepth, halfDepth));
        Vector3 spawnPosition = area.center.position + area.center.rotation * randomOffset;

        GameObject enemy = Instantiate(
            prefab,
            spawnPosition,
            area.center.rotation,
            spawnedEnemyParent);
        spawnedEnemies.Add(enemy);
        return enemy;
    }

    private void OnDrawGizmosSelected()
    {
        if (spawnAreas == null) return;

        foreach (SpawnArea area in spawnAreas)
        {
            if (area == null || area.center == null) continue;

            Gizmos.matrix = area.center.localToWorldMatrix;
            Gizmos.color = Color.red;
            Gizmos.DrawWireCube(Vector3.zero, Vector3.one);
        }

        Gizmos.matrix = Matrix4x4.identity;
    }
}

