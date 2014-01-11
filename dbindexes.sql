SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- TOC entry 184 (class 3079 OID 12595)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- TOC entry 2903 (class 0 OID 0)
-- Dependencies: 184
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

\connect ethea

--
-- TOC entry 2776 (class 2606 OID 17587)
-- Name: communities_itemtypes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY communities_itemtypes
    ADD CONSTRAINT communities_itemtypes_pkey PRIMARY KEY (community_id, itemtype_id);


--
-- TOC entry 2774 (class 2606 OID 17126)
-- Name: communities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY communities
    ADD CONSTRAINT communities_pkey PRIMARY KEY (id);


--
-- TOC entry 2778 (class 2606 OID 17589)
-- Name: communities_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY communities_profiles
    ADD CONSTRAINT communities_profiles_pkey PRIMARY KEY (community_id, profile_id);


--
-- TOC entry 2780 (class 2606 OID 17128)
-- Name: itemlists_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY itemlists
    ADD CONSTRAINT itemlists_pkey PRIMARY KEY (id);


--
-- TOC entry 2783 (class 2606 OID 17130)
-- Name: items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY items
    ADD CONSTRAINT items_pkey PRIMARY KEY (id);


--
-- TOC entry 2785 (class 2606 OID 18122)
-- Name: itemtype_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY itemtypes
    ADD CONSTRAINT itemtype_name_key UNIQUE (name);


--
-- TOC entry 2787 (class 2606 OID 17132)
-- Name: itemtype_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY itemtypes
    ADD CONSTRAINT itemtype_pkey PRIMARY KEY (id);


--
-- TOC entry 2789 (class 2606 OID 17134)
-- Name: messages_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- TOC entry 2791 (class 2606 OID 17136)
-- Name: posts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY posts
    ADD CONSTRAINT posts_pkey PRIMARY KEY (id);


--
-- TOC entry 2793 (class 2606 OID 17595)
-- Name: posts_tags_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY posts_tags
    ADD CONSTRAINT posts_tags_pkey PRIMARY KEY (post_id, tag_id);


--
-- TOC entry 2795 (class 2606 OID 17802)
-- Name: profiles_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY profiles
    ADD CONSTRAINT profiles_name_key UNIQUE (name);


--
-- TOC entry 2797 (class 2606 OID 18118)
-- Name: profiles_name_key1; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY profiles
    ADD CONSTRAINT profiles_name_key1 UNIQUE (name);


--
-- TOC entry 2799 (class 2606 OID 17140)
-- Name: profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY profiles
    ADD CONSTRAINT profiles_pkey PRIMARY KEY (id);


--
-- TOC entry 2801 (class 2606 OID 17142)
-- Name: structures_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY structures
    ADD CONSTRAINT structures_pkey PRIMARY KEY (id);


--
-- TOC entry 2803 (class 2606 OID 17144)
-- Name: suggestion_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY suggestion
    ADD CONSTRAINT suggestion_pkey PRIMARY KEY (id);

ALTER TABLE ONLY ethean_groups
    ADD CONSTRAINT pg_pkey PRIMARY KEY (ethean_id, group_name);
--
-- TOC entry 2805 (class 2606 OID 17146)
-- Name: tags_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY tags
    ADD CONSTRAINT tags_pkey PRIMARY KEY (id);


--
-- TOC entry 2808 (class 2606 OID 17497)
-- Name: etheans_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY etheans
    ADD CONSTRAINT etheans_email_key UNIQUE (email);


--
-- TOC entry 2810 (class 2606 OID 17499)
-- Name: etheans_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY etheans
    ADD CONSTRAINT etheans_name_key UNIQUE (name);


--
-- TOC entry 2812 (class 2606 OID 17148)
-- Name: etheans_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY etheans
    ADD CONSTRAINT etheans_pkey PRIMARY KEY (id);


ALTER TABLE ONLY posts_items
    ADD CONSTRAINT posts_items_pkey PRIMARY KEY (structure_id, item_id);


--
-- TOC entry 2781 (class 1259 OID 17778)
-- Name: items_name_trgm_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX items_name_trgm_idx ON items USING gist (name gist_trgm_ops);


--
-- TOC entry 2806 (class 1259 OID 17149)
-- Name: ethean_name_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX ethean_name_idx ON etheans USING btree (name);


CREATE INDEX group_uuid_idx ON ethean_groups (other_id);


--
-- TOC entry 2813 (class 2606 OID 17150)
-- Name: fk_communities_itemtypes_itemtype_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY communities_itemtypes
    ADD CONSTRAINT fk_communities_itemtypes_itemtype_1 FOREIGN KEY (itemtype_id) REFERENCES itemtypes(id) ON DELETE CASCADE;;


--
-- TOC entry 2815 (class 2606 OID 17155)
-- Name: fk_communities_profiles_communities_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY communities_profiles
    ADD CONSTRAINT fk_communities_profiles_communities_1 FOREIGN KEY (community_id) REFERENCES communities(id) ON DELETE CASCADE;;


--
-- TOC entry 2816 (class 2606 OID 17160)
-- Name: fk_communities_profiles_profiles_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY communities_profiles
    ADD CONSTRAINT fk_communities_profiles_profiles_1 FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE;


--
-- TOC entry 2814 (class 2606 OID 17803)
-- Name: fk_communities_types_communities_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY communities_itemtypes
    ADD CONSTRAINT fk_communities_types_communities_1 FOREIGN KEY (community_id) REFERENCES communities(id) ON DELETE CASCADE;


--
-- TOC entry 2833 (class 2606 OID 17475)
-- Name: fk_itemlists_items_itemlists_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY itemlists_items
    ADD CONSTRAINT fk_itemlists_items_itemlists_1 FOREIGN KEY (itemlist_id) REFERENCES itemlists(id) ON DELETE CASCADE;


--
-- TOC entry 2834 (class 2606 OID 17480)
-- Name: fk_itemlists_items_items_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY itemlists_items
    ADD CONSTRAINT fk_itemlists_items_items_1 FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE;


--
-- TOC entry 2817 (class 2606 OID 17180)
-- Name: fk_itemlists_profiles_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY itemlists
    ADD CONSTRAINT fk_itemlists_profiles_1 FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE;


--
-- TOC entry 2818 (class 2606 OID 17185)
-- Name: fk_items_type_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY items
    ADD CONSTRAINT fk_items_type_1 FOREIGN KEY (itemtype_id) REFERENCES itemtypes(id) ON DELETE CASCADE;


--
-- TOC entry 2819 (class 2606 OID 17190)
-- Name: fk_messages_profiles_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY messages
    ADD CONSTRAINT fk_messages_profiles_1 FOREIGN KEY (from_id) REFERENCES profiles(id) ON DELETE SET NULL;


--
-- TOC entry 2820 (class 2606 OID 17195)
-- Name: fk_messages_profiles_2; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY messages
    ADD CONSTRAINT fk_messages_profiles_2 FOREIGN KEY (to_id) REFERENCES profiles(id) ON DELETE SET NULL;


--
-- TOC entry 2824 (class 2606 OID 17808)
-- Name: fk_posts_communities_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY posts
    ADD CONSTRAINT fk_posts_communities_1 FOREIGN KEY (community_id) REFERENCES communities(id) ON DELETE CASCADE;


--
-- TOC entry 2825 (class 2606 OID 17205)
-- Name: fk_posts_items_items_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY posts_items
    ADD CONSTRAINT fk_posts_items_items_1 FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE SET NULL;


--
-- TOC entry 2826 (class 2606 OID 17818)
-- Name: fk_posts_items_structures_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY posts_items
    ADD CONSTRAINT fk_posts_items_structures_1 FOREIGN KEY (structure_id) REFERENCES structures(id) ON DELETE CASCADE;


ALTER TABLE ONLY ethean_groups
    ADD CONSTRAINT fk_ethean_groups_1 FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE;

ALTER TABLE ONLY ethean_groups
    ADD CONSTRAINT fk_ethean_groups_2 FOREIGN KEY (ethean_id) REFERENCES etheans(id) ON DELETE CASCADE;
--
-- TOC entry 2821 (class 2606 OID 17215)
-- Name: fk_posts_posts_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY posts
    ADD CONSTRAINT fk_posts_posts_1 FOREIGN KEY (parent_id) REFERENCES posts(id) ON DELETE SET NULL;


--
-- TOC entry 2822 (class 2606 OID 17220)
-- Name: fk_posts_posts_2; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY posts
    ADD CONSTRAINT fk_posts_posts_2 FOREIGN KEY (root_id) REFERENCES posts(id) ON DELETE SET NULL;


--
-- TOC entry 2823 (class 2606 OID 17225)
-- Name: fk_posts_profiles_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY posts
    ADD CONSTRAINT fk_posts_profiles_1 FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE SET NULL;


--
-- TOC entry 2827 (class 2606 OID 17230)
-- Name: fk_posts_tags_posts_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY posts_tags
    ADD CONSTRAINT fk_posts_tags_posts_1 FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE;


--
-- TOC entry 2828 (class 2606 OID 17235)
-- Name: fk_posts_tags_tags_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY posts_tags
    ADD CONSTRAINT fk_posts_tags_tags_1 FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE;


--
-- TOC entry 2829 (class 2606 OID 17240)
-- Name: fk_profiles_etheans_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY profiles
    ADD CONSTRAINT fk_profiles_etheans_1 FOREIGN KEY (ethean_id) REFERENCES etheans(id) ON DELETE CASCADE;


--
-- TOC entry 2830 (class 2606 OID 17813)
-- Name: fk_structures_posts_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY structures
    ADD CONSTRAINT fk_structures_posts_1 FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE;


--
-- TOC entry 2831 (class 2606 OID 17250)
-- Name: fk_suggestion_items_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY suggestion
    ADD CONSTRAINT fk_suggestion_items_1 FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE;


--
-- TOC entry 2832 (class 2606 OID 17255)
-- Name: fk_suggestion_profiles_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY suggestion
    ADD CONSTRAINT fk_suggestion_profiles_1 FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE SET NULL;


--
-- TOC entry 2946 (class 0 OID 0)
-- Dependencies: 6
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


-- Completed on 2013-12-23 17:25:09 PST

--
-- PostgreSQL database dump complete
--

