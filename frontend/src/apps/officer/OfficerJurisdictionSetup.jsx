import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  getStates,
  getDistricts,
  getAreas,
  getWards,
  saveOfficerJurisdiction,
} from '../../services/api';
import { Button } from '../../components/ui/Button';
import { GlassCard } from '../../components/ui/GlassCard';

export function OfficerJurisdictionSetup() {
  const navigate = useNavigate();
  const [states, setStates] = useState([]);
  const [districts, setDistricts] = useState([]);
  const [areas, setAreas] = useState([]);
  const [wards, setWards] = useState([]);
  const [stateId, setStateId] = useState('');
  const [districtId, setDistrictId] = useState('');
  const [areaId, setAreaId] = useState('');
  const [wardId, setWardId] = useState('');
  const [additionalWardIds, setAdditionalWardIds] = useState([]);
  const [additionalSelections, setAdditionalSelections] = useState(['']);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadStates = async () => {
      try {
        const data = await getStates();
        setStates(data);
      } catch (err) {
        setError(err.message);
      }
    };

    loadStates();
  }, []);

  useEffect(() => {
    if (!stateId) return;
    const loadDistricts = async () => {
      setLoading(true);
      try {
        const data = await getDistricts(stateId);
        setDistricts(data);
        setAreas([]);
        setWards([]);
        setDistrictId('');
        setAreaId('');
        setWardId('');
        setAdditionalWardIds([]);
        setAdditionalSelections(['']);
      } finally {
        setLoading(false);
      }
    };
    loadDistricts();
  }, [stateId]);

  useEffect(() => {
    if (!districtId) return;
    const loadAreas = async () => {
      setLoading(true);
      try {
        const data = await getAreas(districtId);
        setAreas(data);
        setWards([]);
        setAreaId('');
        setWardId('');
        setAdditionalWardIds([]);
        setAdditionalSelections(['']);
      } finally {
        setLoading(false);
      }
    };
    loadAreas();
  }, [districtId]);

  useEffect(() => {
    if (!areaId) return;
    const loadWards = async () => {
      setLoading(true);
      try {
        const data = await getWards(areaId);
        setWards(data);
        setWardId('');
        setAdditionalWardIds([]);
        setAdditionalSelections(['']);
      } finally {
        setLoading(false);
      }
    };
    loadWards();
  }, [areaId]);

  const addExtraWard = () => {
    setAdditionalSelections((current) => [...current, '']);
  };

  const updateExtraWard = (index, value) => {
    setAdditionalSelections((current) => {
      const next = [...current];
      next[index] = value;
      return next;
    });
  };

  const handleSave = async () => {
    if (!wardId) {
      setError('Please select a ward.');
      return;
    }

    setSaving(true);
    setError('');
    try {
      const extras = additionalSelections.filter(Boolean).map((value) => Number(value));
      await saveOfficerJurisdiction({ ward_id: Number(wardId), additional_ward_ids: extras });
      navigate('/officer', { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div style={{ padding: 24, maxWidth: 900, margin: '0 auto' }}>
      <GlassCard layer={2} style={{ padding: 24 }}>
        <h2 style={{ marginBottom: 8 }}>Set Your Jurisdiction</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: 20 }}>
          Select your primary ward first. Senior officers can add multiple wards.
        </p>

        <div style={{ display: 'grid', gap: 16 }}>
          <label>
            <div style={{ marginBottom: 6 }}>State</div>
            <select className="form-select" value={stateId} onChange={(e) => setStateId(e.target.value)}>
              <option value="">Select state</option>
              {states.map((state) => (
                <option key={state.state_id} value={state.state_id}>{state.state_name}</option>
              ))}
            </select>
          </label>

          <label>
            <div style={{ marginBottom: 6 }}>District</div>
            <select className="form-select" value={districtId} onChange={(e) => setDistrictId(e.target.value)} disabled={!stateId || loading}>
              <option value="">Select district</option>
              {districts.map((district) => (
                <option key={district.district_id} value={district.district_id}>{district.district_name}</option>
              ))}
            </select>
          </label>

          <label>
            <div style={{ marginBottom: 6 }}>Area</div>
            <select className="form-select" value={areaId} onChange={(e) => setAreaId(e.target.value)} disabled={!districtId || loading}>
              <option value="">Select area</option>
              {areas.map((area) => (
                <option key={area.area_id} value={area.area_id}>{area.area_name} ({area.pincode})</option>
              ))}
            </select>
          </label>

          <label>
            <div style={{ marginBottom: 6 }}>Primary Ward</div>
            <select className="form-select" value={wardId} onChange={(e) => setWardId(e.target.value)} disabled={!areaId || loading}>
              <option value="">Select ward</option>
              {wards.map((ward) => (
                <option key={ward.ward_id} value={ward.ward_id}>{ward.ward_number} - {ward.ward_name}</option>
              ))}
            </select>
          </label>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
              <div>Additional Wards</div>
              <Button type="button" variant="outline" onClick={addExtraWard}>Add Jurisdiction</Button>
            </div>
            <div style={{ display: 'grid', gap: 12 }}>
              {additionalSelections.map((value, index) => (
                <select
                  key={index}
                  className="form-select"
                  value={value}
                  onChange={(e) => updateExtraWard(index, e.target.value)}
                  disabled={!areaId || loading}
                >
                  <option value="">Select extra ward</option>
                  {wards.map((ward) => (
                    <option key={ward.ward_id} value={ward.ward_id}>{ward.ward_number} - {ward.ward_name}</option>
                  ))}
                </select>
              ))}
            </div>
          </div>

          {error && <div style={{ color: '#f87171' }}>{error}</div>}

          <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
            <strong>Note:</strong> Admin and senior officers can add multiple wards using the additional jurisdiction list.
          </div>

          <div style={{ display: 'flex', gap: 12 }}>
            <Button type="button" variant="primary" onClick={handleSave} loading={saving}>
              Save Jurisdiction
            </Button>
          </div>
        </div>
      </GlassCard>
    </div>
  );
}
